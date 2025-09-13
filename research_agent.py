#!/usr/bin/env python3
"""Simplified on-demand research agent"""
import json
import argparse
import os
from database_manager import DatabaseManager
from tools.archive.wayback import snapshot


def run(topic: str, hours: float, focus: str, model: str=None, provider: str=None):
    """Execute a research run and store artifacts."""
    with open('config.json') as f:
        config = json.load(f)
    db = DatabaseManager(config.get('database_path', '/root/research.db'))
    content = f"Research on {topic} focusing on {focus}"
    db.add_source(content)
    archived = snapshot('http://example.com')
    os.makedirs('reports', exist_ok=True)
    with open('reports/full_report.md', 'w') as f:
        f.write(f"# Report on {topic}\n\n{content}\n")
    with open('reports/citations.json', 'w') as f:
        json.dump([{'url': 'http://example.com', 'archived_url': archived}], f)
    return {'report': 'reports/full_report.md', 'citations': 'reports/citations.json'}


def main():
    parser = argparse.ArgumentParser(description='Run research agent')
    parser.add_argument('--topic', required=True)
    parser.add_argument('--hours', type=float, default=1)
    parser.add_argument('--focus', default='')
    args = parser.parse_args()
    run(args.topic, args.hours, args.focus)

if __name__ == '__main__':
    main()
