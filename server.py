"""가계부 웹 서버  —  python server.py 로 실행"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, threading, webbrowser

BASE      = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data.json")
HTML_FILE = os.path.join(BASE, "index.html")
PORT      = 8000


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self._serve_html()
        elif self.path == '/api/data':
            self._get_data()
        else:
            self._respond(404, b'Not Found')

    def do_POST(self):
        if self.path == '/api/data':
            self._post_data()
        else:
            self._respond(404, b'Not Found')

    # ── handlers ─────────────────────────────────────────────────────────

    def _serve_html(self):
        with open(HTML_FILE, 'rb') as f:
            body = f.read()
        self._respond(200, body, 'text/html; charset=utf-8')

    def _get_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                body = f.read().encode('utf-8')
        else:
            body = b'{"transactions":[]}'
        self._respond(200, body, 'application/json; charset=utf-8')

    def _post_data(self):
        length = int(self.headers.get('Content-Length', 0))
        raw    = self.rfile.read(length)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(json.loads(raw), f, ensure_ascii=False, indent=2)
        self._respond(200, b'{"ok":true}', 'application/json')

    # ── util ─────────────────────────────────────────────────────────────

    def _respond(self, code, body, ct='text/plain'):
        self.send_response(code)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass  # 요청 로그 숨김


if __name__ == '__main__':
    srv = HTTPServer(('localhost', PORT), Handler)
    url = f'http://localhost:{PORT}'
    print(f'가계부 서버 실행 중: {url}')
    print('종료하려면 Ctrl+C 를 누르세요.\n')
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print('\n서버 종료')
