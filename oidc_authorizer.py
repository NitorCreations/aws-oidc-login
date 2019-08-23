import webbrowser
import uuid
import config
import sys
import requests
try:
    # For Python 3.5 and later
    from urllib.parse import parse_qs
    from urllib.parse import urlparse
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from socketserver import ThreadingMixIn
except ImportError:
    # Python 2.7
    from urlparse import parse_qs
    from urlparse import urlparse
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from SocketServer import ThreadingMixIn


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        pass


class OidcAuthenticationCodeFlowAuthorizer:

    class _RedirectHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            success = False
            query_components = parse_qs(urlparse(self.path).query)
            try:
                if query_components['state'][0] == OidcAuthenticationCodeFlowAuthorizer.state:
                    success = True
                OidcAuthenticationCodeFlowAuthorizer.code_result = query_components['code'][0]
            except KeyError:
                self.fail()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            if not success or 'error' in query_components:
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
        OidcAuthenticationCodeFlowAuthorizer.state = str(uuid.uuid4())
        url = config.AUTHORITY_URL \
            + '/authorize?' \
            + 'client_id={CLIENT_ID}'.format(CLIENT_ID=config.CLIENT_ID) \
            + '&scope={AUTH_SCOPE}'.format(AUTH_SCOPE=config.AUTH_SCOPE) \
            + '&redirect_uri=http://localhost:8401' \
            + '&response_type=code' \
            + '&response_mode=query' \
            + '&state={STATE}'.format(STATE=OidcAuthenticationCodeFlowAuthorizer.state)
        webbrowser.open_new(url)

        with ThreadingHTTPServer(('127.0.0.1', 8401), self._RedirectHandler) as server:
            server.timeout = 30
            while not hasattr(OidcAuthenticationCodeFlowAuthorizer, 'code_result'):
                server.handle_request()
        try:
            code = OidcAuthenticationCodeFlowAuthorizer.code_result
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