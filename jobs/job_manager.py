import asyncio
import threading
import time
import uuid
from typing import Any, Dict, Optional

import research_agent


class JobManager:
    """Manage background research jobs."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.current: Optional[Dict[str, Any]] = None
        self.history = []

    # ------------------------------------------------------------------
    def _run(self, job: Dict[str, Any], topic: str, hours: float, focus: str, config: Optional[Dict[str, Any]]):
        cancel_event = asyncio.Event()

        def progress_cb(message: str, percentage: float) -> None:
            with self._lock:
                job['progress'] = percentage
                job['stage'] = message

        job['cancel_event'] = cancel_event
        try:
            artifacts = research_agent.run(
                topic=topic,
                hours=hours,
                focus=focus,
                progress_callback=progress_cb,
                cancel_event=cancel_event,
                config=config,
            )
            job['state'] = 'complete'
            job['progress'] = 1.0
            job['artifacts'] = artifacts
        except research_agent.CancelledError:
            job['state'] = 'cancelled'
            job['artifacts'] = {}
        except Exception as e:  # pragma: no cover - unexpected errors
            job['state'] = 'error'
            job['artifacts'] = {'error': str(e)}
        finally:
            with self._lock:
                self.history.append(dict(job))
                self.current = job

    # ------------------------------------------------------------------
    def start(self, topic: str, hours: float, focus: str, config: Optional[Dict[str, Any]] = None) -> str:
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
                'artifacts': {},
            }
            self.current = job
            t = threading.Thread(target=self._run, args=(job, topic, hours, focus, config), daemon=True)
            t.start()
            return job_id

    def status(self, job_id: Optional[str] = None) -> Dict[str, Any]:
        with self._lock:
            if not self.current:
                return {'state': 'idle'}
            return dict(self.current)

    def cancel(self, job_id: Optional[str] = None) -> bool:
        with self._lock:
            if self.current and self.current.get('state') == 'running':
                self.current['cancel_event'].set()
                return True
        return False

    # ------------------------------------------------------------------
    def reset_for_test(self) -> None:
        with self._lock:
            self.current = None
            self.history = []


job_manager = JobManager()
