from datetime import datetime
from uuid import uuid4
import zlib
import base64
import sys
import webbrowser
import config
import http.server
# import threading

try:
    # For Python 3.0 and later
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib import urlencode

authnrequest_template = (
                        '<samlp:AuthnRequest '
                                'xmlns="urn:oasis:names:tc:SAML:2.0:metadata" '
                                'ID="{id}" '
                                'Version="2.0" '
                                'IssueInstant="{issue_instant}" '
                                'IsPassive="false" '
                                'AssertionConsumerServiceURL="{assertion_consumer_service_url}" '
                                'xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" '
                                'ForceAuthn="false">'
                            '<Issuer xmlns="urn:oasis:names:tc:SAML:2.0:assertion">{issuer_url}</Issuer>'
                            '<samlp:NameIDPolicy Format="urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"></samlp:NameIDPolicy>'
                        '</samlp:AuthnRequest>'
                        )


def decode_base64_and_inflate(b64string):
    decoded = base64.b64decode(b64string)
    try:
        result = zlib.decompress(decoded, -15)
    except Exception:
        result = decoded
    return result.decode('utf-8')    


def deflate_and_base64_encode(string_val):
    return base64.b64encode(zlib.compress(string_val.encode('utf-8'))[2:-4])


def authn_request(issuer_url, assertion_consumer_service_url='https://signin.aws.amazon.com/saml'):
    """
    Generates an SAML AuthNRequest with AWS as Service Provider
    """
    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    uuid = '_' + str.upper(str(uuid4())).replace('-', '')
    # uuid = str.upper(str(uuid4())).replace('-', '')
    request_payload = authnrequest_template.format(
        id=uuid, 
        issue_instant=now, 
        assertion_consumer_service_url=assertion_consumer_service_url,
        issuer_url=issuer_url)
    print(request_payload)
    return deflate_and_base64_encode(request_payload)

class SamlPostHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(post_data)
        # query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        try:
            SamlPostHandler.saml_response = post_data
        except:
            self.fail()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # if 'error' in query_components:
        #     self.wfile.write(bytes("An error occured. Check the request URL for details.", "UTF-8"))
        # else:
        self.wfile.write(bytes("Login done. You can close this window or tab and crawl back to your shell.",
                                   "UTF-8"))

    def fail(self):
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes("Didn't get SAML Response", "UTF-8"))

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    request = authn_request(sys.argv[1], "http://localhost:8401")
    print(request)
    encoded=urlencode({'SAMLRequest': request})
    print(encoded)
    url = config.AAD_IDP_URL + '?' + encoded
    print(url)
    webbrowser.open_new(url)

    with http.server.ThreadingHTTPServer(('127.0.0.1', 8402), SamlPostHandler) as server:
        server.timeout = 30
        while not hasattr(SamlPostHandler, 'saml_response'):
            server.handle_request()
    try:
        saml_response = SamlPostHandler.saml_response
        print(saml_response)
    except AttributeError:
        print("Failed to get authorization code from AAD. Try again?")
        exit(1)