import json
import os
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from jobs.job_manager import job_manager
from chatbot_engine import get_engine
from user_manager import user_manager
from tools.emailer import send_file

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

def handle_run(data, db_path=None):
    topic = data.get('topic', CONFIG['ui'].get('default_topic'))
    hours = float(data.get('hours', CONFIG['ui'].get('default_hours', 1)))
    focus = data.get('focus', CONFIG['ui'].get('default_focus', ''))
    model = data.get('model')
    provider = data.get('provider')
    job_id = job_manager.start(topic, hours, focus, model=model, provider=provider, db_path=db_path)
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
                self.load_session()
                if not self.session.get('username'):
                    self.send_response(200)
                    with open('templates/login.html', 'rb') as f:
                        content = f.read()
                    self.end_headers()
                    self.wfile.write(content)
                    return
                self.send_response(200)
                with open('templates/index.html', 'rb') as f:
                    content = f.read()
                self.end_headers()
                self.wfile.write(content)
            elif self.path == '/research':
                self.send_response(200)
                self.load_session()
                if not self.session.get('username'):
                    self.send_header('Location', '/')
                    self.end_headers()
                    return
                handle_index()
                with open('templates/research.html', 'rb') as f:
                    content = f.read()
                self.end_headers()
                self.wfile.write(content)
            elif self.path == '/chat':
                self.send_response(200)
                self.load_session()
                if not self.session.get('username'):
                    self.send_header('Location', '/')
                    self.end_headers()
                    return
                with open('templates/chat.html', 'rb') as f:
                    content = f.read()
                self.end_headers()
                self.wfile.write(content)
            elif self.path == '/status':
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps(handle_status()).encode())
            elif self.path == '/logout':
                self.load_session()
                self.session.pop('username', None)
                self.session.pop('db_path', None)
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
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
                self.load_session()
                res = handle_run(payload, self.session.get('db_path'))
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
            elif self.path == '/login':
                params = parse_qs(data.decode())
                action = params.get('action', ['login'])[0]
                user = params.get('username', [''])[0]
                pw = params.get('password', [''])[0]
                email = params.get('email', [''])[0] or None
                if action == 'register':
                    if not user_manager.register(user, pw, email):
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(b'User exists')
                        return
                elif not user_manager.authenticate(user, pw):
                    self.send_response(401)
                    self.end_headers()
                    self.wfile.write(b'Invalid credentials')
                    return
                self.load_session()
                self.session['username'] = user
                self.session['db_path'] = user_manager.db_path(user)
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
                return
            elif self.path == '/email_db':
                self.load_session()
                to = payload.get('to') or user_manager.email(self.session.get('username', ''))
                if to:
                    send_file(self.session.get('db_path'), to, CONFIG.get('email', {}))
                    res = {'sent': True}
                else:
                    res = {'sent': False}
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
