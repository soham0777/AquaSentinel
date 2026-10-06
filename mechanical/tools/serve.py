"""Local preview server for the AquaSentinel R3 design folder.
GET  serves files from AquaSentinel_Design/
POST /save?path=<renders|animation|drawings|checks>/<file>  writes the request body (used to save renders and recordings)
"""
import http.server
import os
import socketserver
import sys
import urllib.parse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ALLOWED = ("renders", "animation", "drawings", "checks", "viewer")


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_POST(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        rel = os.path.normpath(q.get("path", [""])[0]).replace("\\", "/")
        if not rel or rel.startswith("..") or rel.split("/")[0] not in ALLOWED:
            self.send_response(403)
            self.end_headers()
            return
        n = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(n)
        out = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "wb") as f:
            f.write(data)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(f"saved {rel} {len(data)}".encode())

    def log_message(self, fmt, *args):
        if "POST" in (fmt % args):
            sys.stderr.write((fmt % args) + "\n")


class TS(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    with TS(("127.0.0.1", port), H) as httpd:
        print(f"serving {ROOT} on http://127.0.0.1:{port}")
        httpd.serve_forever()
