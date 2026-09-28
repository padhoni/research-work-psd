from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json
from analysis import analyze, simulate, DEMO

ROOT = Path(__file__).parent / 'static'
class Handler(BaseHTTPRequestHandler):
    def respond(self, status, data, kind='application/json'):
        body = data.encode() if isinstance(data, str) else json.dumps(data, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', kind + '; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        routes = {'/': ('index.html','text/html'), '/paper': ('paper.html','text/html'), '/app.js': ('app.js','text/javascript'), '/style.css': ('style.css','text/css')}
        if self.path == '/api/demo':
            return self.respond(200, {'csv': DEMO})
        if self.path == '/api/synthetic-5000':
            return self.respond(200, {'csv': (ROOT.parent/'examples/documentation.csv').read_text(), 'source': 'simulated'})
        if self.path == '/api/publication':
            return self.respond(200, json.loads((ROOT.parent/'publication/results.json').read_text()))
        if self.path not in routes:
            return self.respond(404, {'error':'Not found'})
        file, mime = routes[self.path]
        self.respond(200, (ROOT/file).read_text(), mime)
    def do_POST(self):
        # Reject cross-origin browser requests; bind only to localhost.
        if self.headers.get('Origin') and self.headers['Origin'] != 'http://' + self.headers.get('Host',''):
            return self.respond(403, {'error':'Cross-origin requests are not supported.'})
        try:
            size = int(self.headers.get('Content-Length','0'))
            if not 0 < size <= 2000000:
                raise ValueError('Request must be under 2 MB.')
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError('Request body must be a JSON object.')
            if self.path == '/api/analyze':
                result = analyze(data['csv'], data.get('metric','time'), data.get('source','simulated'))
            elif self.path == '/api/simulate':
                result = simulate(data['seed'], data['n'], float(data['legacy'])/100, float(data['ai'])/100)
            else:
                return self.respond(404, {'error':'Not found'})
            self.respond(200, result)
        except (ValueError, KeyError, TypeError, AttributeError, OverflowError) as exc:
            self.respond(400, {'error':str(exc)})
    def log_message(self, fmt, *args):
        pass  # No request or dataset logging.

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    print(f'EPIC Research Lab: http://127.0.0.1:{args.port}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
