import json
import os
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from jobs.job_manager import job_manager
from chatbot_engine import get_engine

with open('config.json') as _f:
    CONFIG = json.load(_f)
autostarted = False
sessions = {}

def handle_index():
    global autostarted
    if (CONFIG.get('ui', {}).get('autostart_on_open') and
        (not autostarted or not CONFIG['ui'].get('autostart_once_per_process')) and
        not job_manager.active() and
        job_manager.acquire_autostart_lock()):
        job_manager.start(
            CONFIG['ui'].get('default_topic', ''),
            CONFIG['ui'].get('default_hours', 1),
            CONFIG['ui'].get('default_focus', '')
        )
        autostarted = True
    return "OK"

def handle_run(data):
    topic = data.get('topic', CONFIG['ui'].get('default_topic'))
    hours = float(data.get('hours', CONFIG['ui'].get('default_hours', 1)))
    focus = data.get('focus', CONFIG['ui'].get('default_focus', ''))
    model = data.get('model')
    provider = data.get('provider')
    job_id = job_manager.start(topic, hours, focus, model=model, provider=provider)
    return {'job_id': job_id}

def handle_cancel():
    return {'cancelled': job_manager.cancel()}

def handle_status():
    return job_manager.status()

def run_server(config=None):
    global CONFIG
    if config is None:
        with open('config.json') as f:
            CONFIG = json.load(f)
    else:
        CONFIG = config
    engine = get_engine(CONFIG)

    class Handler(BaseHTTPRequestHandler):
        def load_session(self):
            cookie = self.headers.get('Cookie', '')
            sid = None
            for part in cookie.split(';'):
                if part.strip().startswith('sid='):
                    sid = part.strip()[4:]
            if not sid or sid not in sessions:
                sid = str(uuid.uuid4())
                sessions[sid] = {
                    'mode': CONFIG.get('chatbot', {}).get('default_mode', 'research'),
                    'uncensored': CONFIG.get('chatbot', {}).get('force_uncensored', False)
                }
            self.send_header('Set-Cookie', f'sid={sid}; Path=/')
            self.sid = sid
            self.session = sessions[sid]

        def do_GET(self):
            if self.path == '/':
                self.send_response(200)
                self.load_session()
                with open('templates/index.html', 'rb') as f:
                    content = f.read()
                self.end_headers()
                self.wfile.write(content)
            elif self.path == '/research':
                self.send_response(200)
                self.load_session()
                handle_index()
                with open('templates/research.html', 'rb') as f:
                    content = f.read()
                self.end_headers()
                self.wfile.write(content)
            elif self.path == '/chat':
                self.send_response(200)
                self.load_session()
                with open('templates/chat.html', 'rb') as f:
                    content = f.read()
                self.end_headers()
                self.wfile.write(content)
            elif self.path == '/status':
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps(handle_status()).encode())
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(length)
            try:
                payload = json.loads(data.decode()) if data else {}
            except Exception:
                payload = {}
            if self.path == '/run':
                res = handle_run(payload)
            elif self.path == '/cancel':
                res = handle_cancel()
            elif self.path == '/chat/send':
                self.load_session()
                msg = payload.get('message', '')
                reply = engine.chat(self.sid, msg, uncensored=self.session.get('uncensored', False))
                res = {'reply': reply}
            elif self.path == '/select':
                params = parse_qs(data.decode())
                mode = params.get('mode', ['research'])[0]
                unc = params.get('uncensored', ['0'])[0] == '1'
                self.load_session()
                self.session['mode'] = mode
                self.session['uncensored'] = unc
                self.send_response(302)
                location = '/chat' if mode == 'chatbot' else '/research'
                self.send_header('Location', location)
                self.end_headers()
                return
            else:
                self.send_response(404)
                self.end_headers()
                return
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(res).encode())

    server = HTTPServer(('0.0.0.0', 7777), Handler)
    server.serve_forever()

if __name__ == '__main__':
    run_server()
