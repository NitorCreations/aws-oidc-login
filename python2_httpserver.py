from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        pass
