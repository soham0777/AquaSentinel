# Serves 10_VIRTUAL_STORYTELLER and accepts POST /frame/<n> (PNG body) -> 04_story_video/frames/<n>.png
import http.server, os, sys, re

ROOT = r'C:\Users\dell\OneDrive\Desktop\AquaSentinel\10_VIRTUAL_STORYTELLER'
FRAMES = os.path.join(ROOT, '04_story_video', 'frames')
os.makedirs(FRAMES, exist_ok=True)


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def do_POST(self):
        m = re.match(r'^/frame/(\d+)$', self.path)
        if not m:
            self.send_response(404); self.end_headers(); return
        n = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(n)
        with open(os.path.join(FRAMES, '%05d.jpg' % int(m.group(1))), 'wb') as f:
            f.write(data)
        self.send_response(200); self.send_header('Content-Type', 'text/plain'); self.end_headers(); self.wfile.write(b'ok')

    def log_message(self, *a):
        pass


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8770
http.server.ThreadingHTTPServer(('127.0.0.1', port), H).serve_forever()
