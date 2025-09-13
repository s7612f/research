import json
from jobs.job_manager import job_manager

with open('config.json') as f:
    CONFIG = json.load(f)

autostarted = False

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

def run_server():
    from http.server import BaseHTTPRequestHandler, HTTPServer
    import json as _json

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self_inner):
            if self_inner.path == '/':
                handle_index()
                self_inner.send_response(200)
                self_inner.end_headers()
                self_inner.wfile.write(b'OK')
            elif self_inner.path == '/status':
                self_inner.send_response(200)
                self_inner.end_headers()
                self_inner.wfile.write(_json.dumps(handle_status()).encode())
            else:
                self_inner.send_response(404)
                self_inner.end_headers()

        def do_POST(self_inner):
            length = int(self_inner.headers.get('Content-Length', 0))
            data = self_inner.rfile.read(length)
            try:
                payload = _json.loads(data.decode()) if data else {}
            except Exception:
                payload = {}
            if self_inner.path == '/run':
                res = handle_run(payload)
            elif self_inner.path == '/cancel':
                res = handle_cancel()
            else:
                self_inner.send_response(404)
                self_inner.end_headers()
                return
            self_inner.send_response(200)
            self_inner.end_headers()
            self_inner.wfile.write(_json.dumps(res).encode())

    server = HTTPServer(('0.0.0.0', 7777), Handler)
    server.serve_forever()

if __name__ == '__main__':
    run_server()
