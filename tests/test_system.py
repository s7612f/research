import os
import time

from jobs.job_manager import job_manager
import web_interface
from database_manager import DatabaseManager
from tools.archive.wayback import snapshot


def test_no_schedule():
    with open('setup.sh') as f:
        text = f.read().lower()
    assert 'cron' not in text


def test_autostart_once():
    job_manager.reset_for_test()
    web_interface.autostarted = False
    web_interface.handle_index()
    first_count = job_manager.run_count
    web_interface.handle_index()
    assert job_manager.run_count == first_count


def test_manual_run():
    job_manager.reset_for_test()
    web_interface.autostarted = False
    web_interface.handle_run({"topic": "Test", "hours": 1, "focus": "focus"})
    time.sleep(0.5)
    assert os.path.exists('reports/full_report.md')


def test_archiving():
    url = snapshot('http://example.com')
    assert 'web.archive.org' in url


def test_dedupe(tmp_path):
    db = DatabaseManager(str(tmp_path / 'test.db'))
    db.add_source('same content')
    db.add_source('same content')
    assert db.count_sources() == 1
