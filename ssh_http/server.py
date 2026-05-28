import sys
from http.server import BaseHTTPRequestHandler, HTTPServer


class App(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

        self.wfile.write(f"""
Hello World!
@Samsung Server

Client: {self.client_address}
Path: {self.path}
""".encode())


if __name__ == "__main__":
    # systemd socket activation passa o socket pronto
    httpd = HTTPServer(("0.0.0.0", 0), App, False)

    # reaproveita socket do systemd
    httpd.socket = sys.stdin
    httpd.server_bind = lambda: None
    httpd.server_activate = lambda: None

    httpd.serve_forever()
