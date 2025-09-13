import threading
import time
import uuid
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

import research_agent

class JobManager:
    def __init__(self):
        self._lock = threading.Lock()
        self.current: Optional[Dict[str, Any]] = None
        self.run_count = 0
        self.lock_file = Path('data/locks/autostart.lock')
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        if self.lock_file.exists():
            self.lock_file.unlink()

    def _run(self, job, topic, hours, focus, model, provider):
        try:
            artifacts = research_agent.run(topic=topic, hours=hours, focus=focus,
                                           model=model, provider=provider)
            job['state'] = 'complete'
            job['progress'] = 1.0
            job['artifacts'] = artifacts
        except Exception as e:
            job['state'] = 'error'
            job['artifacts'] = {'error': str(e)}
        finally:
            with self._lock:
                self.current = job
            if self.lock_file.exists():
                try:
                    self.lock_file.unlink()
                except OSError:
                    pass

    def start(self, topic: str, hours: float, focus: str, model: Optional[str]=None, provider: Optional[str]=None) -> str:
        with self._lock:
            if self.current and self.current.get('state') == 'running':
                return self.current['id']
            job_id = str(uuid.uuid4())
            job = {
                'id': job_id,
                'state': 'running',
                'topic': topic,
                'started_at': time.time(),
                'progress': 0.0,
                'artifacts': {}
            }
            self.current = job
            self.run_count += 1
            t = threading.Thread(target=self._run, args=(job, topic, hours, focus, model, provider), daemon=True)
            t.start()
            return job_id

    def status(self, job_id: Optional[str]=None) -> Dict[str, Any]:
        with self._lock:
            if not self.current:
                return {'state': 'idle'}
            return dict(self.current)

    def cancel(self, job_id: Optional[str]=None) -> bool:
        # Best-effort: we can't cancel threads; mark state
        with self._lock:
            if self.current and self.current.get('state') == 'running':
                self.current['state'] = 'error'
                self.current['artifacts'] = {'error': 'cancelled'}
                return True
        return False

    def active(self) -> bool:
        with self._lock:
            return self.current is not None and self.current.get('state') == 'running'

    def acquire_autostart_lock(self) -> bool:
        try:
            fd = os.open(self.lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return True
        except FileExistsError:
            return False

    # Test helper
    def reset_for_test(self):
        with self._lock:
            self.current = None
            self.run_count = 0
        if self.lock_file.exists():
            try:
                self.lock_file.unlink()
            except OSError:
                pass

job_manager = JobManager()
