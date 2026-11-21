"""Small web server for the dashboard (standard library only, works offline at the booth).

  GET  /              the dashboard
  GET  /api/state     full snapshot with the last 10 minutes of readings
  GET  /api/stream    live updates (Server-Sent Events), one per reading
  POST /api/cmd       {"action": "beacon_test" | "sample" | "sms_test" | "relearn", "arg": ...}
  GET  /api/csv       today's readings as a CSV download
"""
import json
import os
import queue
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

WEB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web")
TYPES = {".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "application/javascript",
         ".svg": "image/svg+xml", ".png": "image/png", ".ico": "image/x-icon"}


def make_handler(station):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, code, body, ctype="application/json"):
            data = body if isinstance(body, bytes) else body.encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            path = self.path.split("?")[0]
            if path == "/api/state":
                return self._send(200, json.dumps(station.snapshot()))
            if path == "/api/stream":
                return self._stream()
            if path == "/api/csv":
                f = os.path.join(station.cfg["log_dir"], time.strftime("readings_%Y-%m-%d.csv"))
                if os.path.exists(f):
                    with open(f, "rb") as fh:
                        return self._send(200, fh.read(), "text/csv")
                return self._send(404, "{}")
            name = "index.html" if path in ("/", "") else path.lstrip("/")
            full = os.path.normpath(os.path.join(WEB, name))
            if not full.startswith(WEB) or not os.path.isfile(full):
                return self._send(404, "not found", "text/plain")
            with open(full, "rb") as fh:
                return self._send(200, fh.read(), TYPES.get(os.path.splitext(full)[1], "application/octet-stream"))

        def do_POST(self):
            if self.path != "/api/cmd":
                return self._send(404, "{}")
            try:
                n = int(self.headers.get("Content-Length", 0))
                req = json.loads(self.rfile.read(n) or b"{}")
                res = station.command(req.get("action"), req.get("arg"))
            except Exception as e:
                res = f"error: {e}"
            return self._send(200, json.dumps({"result": res}))

        def _stream(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            q = queue.Queue(maxsize=20)
            station.listeners.append(q)
            try:
                while True:
                    try:
                        data = q.get(timeout=15)
                        self.wfile.write(b"data: " + data.encode() + b"\n\n")
                    except queue.Empty:
                        self.wfile.write(b": keep-alive\n\n")
                    self.wfile.flush()
            except Exception:
                pass
            finally:
                if q in station.listeners:
                    station.listeners.remove(q)

    return H


def serve(station, port):
    srv = ThreadingHTTPServer(("0.0.0.0", port), make_handler(station))
    srv.daemon_threads = True
    station.log(f"Dashboard on http://localhost:{port}  (other devices on the same Wi-Fi: http://<pi-address>:{port})")
    srv.serve_forever()
