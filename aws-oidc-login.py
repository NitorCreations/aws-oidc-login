import sys
import webbrowser
import config
import threading
import json
# pypi dependencies
import boto3
import requests

try:
    # For Python 3.0 and later
    from urllib.parse import urlencode
    from urllib.parse import parse_qs
    from urllib.parse import unquote
    from urllib.parse import urlparse
    from urllib.parse import quote_plus
    from http.server import BaseHTTPRequestHandler
    from http.server import ThreadingHTTPServer as ThreadingHTTPServer
except ImportError:
    # Fall back to Python 2
    from urllib import urlencode  # noqa: F401
    from urlparse import parse_qs
    from urlparse import unquote  # noqa: F401
    from urlparse import urlparse
    from urllib import quote_plus
    from python2_httpserver import ThreadingHTTPServer as ThreadingHTTPServer
    from BaseHTTPServer import BaseHTTPRequestHandler
    # TODO solve http server python 2


aws_sts = boto3.client('sts')


class AADAuthenticationCodeFlowAuthorizer:
    thread_lock = threading.Lock()

    class _RedirectHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            query_components = parse_qs(urlparse(self.path).query)
            try:
                AADAuthenticationCodeFlowAuthorizer.code_result = query_components['code'][0]
            except KeyError:
                self.fail()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            if 'error' in query_components:
                self.wfile.write(self._prepare_output('An error occured. Check the request URL for details.'))
            else:
                self.wfile.write(self._prepare_output(('Login done. You can close this window or tab '
                                                       'and crawl back to your shell.')))

        def fail(self):
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self._prepare_output("Didn't get authorization code in query parameter 'code'."))

        def log_message(self, format, *args):
            return

        def _prepare_output(self, output):
            if (sys.version_info > (3, 0)):
                return bytes(output, "UTF-8")
            else:
                return output

    def get_access_token(self):
        url = config.AUTHORITY_URL \
            + '/authorize?' \
            + 'client_id={CLIENT_ID}'.format(CLIENT_ID=config.CLIENT_ID) \
            + '&scope={AUTH_SCOPE}'.format(AUTH_SCOPE=config.AUTH_SCOPE) \
            + '&redirect_uri=http://localhost:8401' \
            + '&response_type=code' \
            + '&response_mode=query' \
            + '&state=12345'
        webbrowser.open_new(url)

        # with AADAuthenticationCodeFlowAuthorizer.thread_lock:
        with ThreadingHTTPServer(('127.0.0.1', 8401), self._RedirectHandler) as server:
            server.timeout = 30
            while not hasattr(AADAuthenticationCodeFlowAuthorizer, 'code_result'):
                server.handle_request()
        try:
            code = AADAuthenticationCodeFlowAuthorizer.code_result
        except AttributeError:
            print("Failed to get authorization code from AAD. Try again?")
            exit(1)

        session = requests.Session()
        resp = session.post(config.AUTHORITY_URL + '/token',
                            data={'client_id': config.CLIENT_ID,
                                  'scope': config.AUTH_SCOPE,
                                  'code': code,
                                  'redirect_uri': 'http://localhost:8401',
                                  'grant_type': 'authorization_code'
                                  })
        token = resp.json()
        return token["id_token"]


def web_console_login(assumed_role_object, session_duration=3600):
    # This code nostly from
    # https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_enable-console-custom-url.html

    url_credentials = {}
    url_credentials['sessionId'] = assumed_role_object.get('Credentials').get('AccessKeyId')
    url_credentials['sessionKey'] = assumed_role_object.get('Credentials').get('SecretAccessKey')
    url_credentials['sessionToken'] = assumed_role_object.get('Credentials').get('SessionToken')
    json_string_with_temp_credentials = json.dumps(url_credentials)

    # Make request to AWS federation endpoint to get sign-in token.
    request_parameters = "?Action=getSigninToken"
    request_parameters += "&SessionDuration={duration}".format(duration=session_duration)
    request_parameters += "&Session=" + quote_plus(json_string_with_temp_credentials)
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters
    r = requests.get(request_url)
    signin_token = json.loads(r.text)

    # Create URL where users can use the sign-in token to sign in to the console.
    request_parameters = "?Action=login"
    request_parameters += "&Issuer=Example.org"
    request_parameters += "&Destination=" + quote_plus("https://console.aws.amazon.com/")
    request_parameters += "&SigninToken=" + signin_token["SigninToken"]
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters

    return request_url


if __name__ == "__main__":
    oidc = AADAuthenticationCodeFlowAuthorizer()
    token = oidc.get_access_token()

    print("Assuming role...")
    response = aws_sts.assume_role_with_web_identity(
        RoleArn=sys.argv[1],
        RoleSessionName="aws-oidc-login-session",
        WebIdentityToken=token,
        DurationSeconds=3600
    )
    print(response)
    login_url = web_console_login(response, session_duration=3600)
    print("console login url: {url}".format(url=login_url))
