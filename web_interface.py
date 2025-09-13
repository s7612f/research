import asyncio
from types import SimpleNamespace

from jobs.job_manager import job_manager

try:  # optional FastAPI import
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.testclient import TestClient
    from pydantic import BaseModel
except Exception:  # fallback stubs when FastAPI isn't available
    FastAPI = None
    WebSocket = object
    WebSocketDisconnect = Exception
    TestClient = None

    class BaseModel:
        def __init__(self, **data):
            for k, v in data.items():
                setattr(self, k, v)


class ResearchRequest(BaseModel):
    topic: str
    hours: float = 1.0
    focus: str = ""


def start_research(req: ResearchRequest):
    job_id = job_manager.start(req.topic, req.hours, req.focus)
    return {"job_id": job_id}


def get_status(job_id: str):
    return job_manager.status(job_id)


if FastAPI:
    app = FastAPI()

    @app.post("/research/start")
    async def _start(req: ResearchRequest):
        return start_research(req)

    @app.get("/research/{job_id}/status")
    async def _status(job_id: str):
        return get_status(job_id)

    @app.websocket("/ws/{job_id}")
    async def websocket_endpoint(websocket: WebSocket, job_id: str):
        await websocket.accept()
        try:
            while True:
                await asyncio.sleep(0.1)
                await websocket.send_json(get_status(job_id))
                state = get_status(job_id).get("state")
                if state in {"complete", "error", "cancelled", "idle"}:
                    break
        except WebSocketDisconnect:  # pragma: no cover - network disconnect
            pass
        finally:
            await websocket.close()

    client = TestClient(app)
else:
    app = None

    class _Resp:
        def __init__(self, data):
            self._data = data

        def json(self):
            return self._data

    class _Client:
        def post(self, path, json):
            return _Resp(start_research(ResearchRequest(**json)))

        def get(self, path):
            job_id = path.strip("/").split("/")[1]
            return _Resp(get_status(job_id))

    client = _Client()
