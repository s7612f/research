import os
import time
import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import research_agent
from database_manager import DatabaseManager
from jobs.job_manager import job_manager
from tools.archive.wayback import snapshot
import web_interface


def sample_config(tmp_path):
    return {
        "llm": {"base_url": "http://localhost:11434", "model": "dolphin-mixtral:8x7b", "temperature": 0.7, "max_tokens": 100, "timeout": 5, "retry_attempts": 1},
        "embedding": {"model": "all-MiniLM-L6-v2", "dimension": 384},
        "research": {"max_iterations": 10, "min_sources": 1, "max_sources": 5, "depth_levels": 1, "enable_controversial": True, "fact_check_threshold": 0.8},
        "scraping": {"rate_limit": 1, "timeout": 5, "user_agents": [], "proxy_list": []},
        "database": {"path": str(tmp_path / "test.db"), "backup_interval": 3600, "connection_pool_size": 1},
    }


def test_database_schema(tmp_path):
    db = DatabaseManager(str(tmp_path / "test.db"))
    cur = db.conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {r[0] for r in cur.fetchall()}
    assert "research_sessions" in tables
    assert "sources" in tables


def test_dedupe(tmp_path):
    db = DatabaseManager(str(tmp_path / "test.db"))
    db.add_source("http://a", "same content")
    db.add_source("http://b", "same content")
    assert db.count_sources() == 1


def test_archiving():
    url = snapshot("http://example.com")
    assert "web.archive.org" in url


def test_job_lifecycle(tmp_path, monkeypatch):
    cfg = sample_config(tmp_path)
    monkeypatch.setattr(research_agent, "load_config", lambda: cfg)
    job_manager.reset_for_test()
    client = web_interface.client
    resp = client.post("/research/start", json={"topic": "Test", "hours": 0.1, "focus": ""})
    job_id = resp.json()["job_id"]
    for _ in range(50):
        status = client.get(f"/research/{job_id}/status").json()
        if status["state"] != "running":
            break
        time.sleep(0.1)
    assert status["state"] == "complete"
    assert os.path.exists(status["artifacts"]["report"])


def test_cancel(tmp_path, monkeypatch):
    cfg = sample_config(tmp_path)
    monkeypatch.setattr(research_agent, "load_config", lambda: cfg)
    job_manager.reset_for_test()
    job_id = job_manager.start("Topic", 1, "")
    time.sleep(0.1)
    assert job_manager.cancel(job_id)
    time.sleep(0.2)
    status = job_manager.status(job_id)
    assert status["state"] in {"cancelled", "complete"}
