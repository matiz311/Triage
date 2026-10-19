"""Local-only demo server. Put authentication/TLS in front before deployment."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import json
from .engine import batch

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # do not log ticket payloads

    def respond(self, code, body, kind='application/json'):
        self.send_response(code)
        self.send_header('Content-Type', kind + '; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self):
        if self.path == '/':
            self.respond(200, Path(__file__).with_name('index.html').read_text(), 'text/html')
        elif self.path == '/health':
            self.respond(200, '{"status":"ok"}')
        else:
            self.respond(404, '{"error":"not found"}')

    def do_POST(self):
        if self.path != '/api/triage':
            return self.respond(404, '{"error":"not found"}')
        # reject browser cross-origin requests; no CORS and no remote exposure
        if self.headers.get('Sec-Fetch-Site') == 'cross-site' or (self.headers.get('Origin') and self.headers['Origin'] != 'http://' + self.headers.get('Host', '')):
            return self.respond(403, '{"error":"origin rejected"}')
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 2000000:
                raise ValueError('Payload vuoto o superiore a 2 MB')
            result = batch(json.loads(self.rfile.read(size)))
            self.respond(200, json.dumps(result, ensure_ascii=False))
        except (ValueError, TypeError, UnicodeError) as exc:
            self.respond(400, json.dumps({'error': str(exc)}))

if __name__ == '__main__':
    print('Triage: http://127.0.0.1:8765 — demo locale')
    HTTPServer(('127.0.0.1', 8765), Handler).serve_forever()
