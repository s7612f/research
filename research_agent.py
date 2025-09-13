"""Core research agent with asynchronous research loop."""

import asyncio
import json
import os
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from database_manager import DatabaseManager
from tools.archive.wayback import snapshot


# ---------------------------------------------------------------------------
class CancelledError(Exception):
    """Raised when a research run is cancelled."""


@dataclass
class OllamaClient:
    config: Dict[str, Any]

    async def analyze(self, content: str, instruction: str) -> Dict[str, Any]:
        """Dummy analysis implementation."""
        await asyncio.sleep(0.01)
        return {"summary": content[:100], "instruction": instruction}

    async def synthesize(self, findings: List[Dict[str, Any]]) -> str:
        await asyncio.sleep(0.01)
        return "\n".join(f["content"] for f in findings)


class EnhancedScraper:
    async def deep_scrape(self, query: str) -> List[str]:
        await asyncio.sleep(0.01)
        return ["http://example.com"]

    async def extract_content(self, url: str) -> str:
        await asyncio.sleep(0.01)
        return "Example content from " + url


class FactChecker:
    async def verify(self, claim: str, sources: List[str]) -> Dict[str, Any]:
        await asyncio.sleep(0.01)
        return {"claim": claim, "verified": True}


class ProgressTracker:
    stages = [
        "initializing",
        "generating_questions",
        "searching_sources",
        "analyzing_content",
        "checking_facts",
        "detecting_contradictions",
        "building_knowledge_graph",
        "generating_report",
    ]

    def __init__(self, callback: Optional[Callable[[str, float], None]] = None):
        self.callback = callback
        self.current_stage = 0

    async def update(self, message: str, percentage: float) -> None:
        if self.callback:
            self.callback(message, percentage)


class ResearchAgent:
    def __init__(
        self,
        config: Dict[str, Any],
        db_manager: DatabaseManager,
        progress_callback: Optional[Callable[[str, float], None]] = None,
        cancel_event: Optional[asyncio.Event] = None,
    ) -> None:
        self.config = config
        self.db = db_manager
        self.llm = OllamaClient(config.get("llm", {}))
        self.scraper = EnhancedScraper()
        self.fact_checker = FactChecker()
        self.progress = ProgressTracker(progress_callback)
        self.cancel_event = cancel_event

    async def run_research(self, topic: str, hours: float, focus: str) -> Dict[str, Any]:
        session_id = self.db.start_session(topic, focus, self.config)
        findings: List[Dict[str, Any]] = []
        for idx, stage in enumerate(self.progress.stages):
            if self.cancel_event and self.cancel_event.is_set():
                self.db.complete_session(session_id, "cancelled")
                raise CancelledError()
            await self.progress.update(stage, idx / len(self.progress.stages))
            await asyncio.sleep(0.05)
        # minimal example: scrape one source and record finding
        urls = await self.scraper.deep_scrape(topic)
        for url in urls:
            content = await self.scraper.extract_content(url)
            source_id, _ = self.db.add_source(url, content)
            self.db.add_finding(session_id, content, 0.5, source_id=source_id)
            findings.append({"content": content, "source_id": source_id})
        report_content = await self.llm.synthesize(findings)
        self.db.complete_session(session_id, "complete")
        os.makedirs("reports", exist_ok=True)
        report_path = os.path.join("reports", "full_report.md")
        with open(report_path, "w") as f:
            f.write(report_content)
        citations_path = os.path.join("reports", "citations.json")
        with open(citations_path, "w") as f:
            json.dump([{"url": u, "archived_url": snapshot(u)} for u in urls], f)
        await self.progress.update("generating_report", 1.0)
        return {
            "session_id": session_id,
            "report": report_path,
            "citations": citations_path,
        }


# ---------------------------------------------------------------------------
def load_config() -> Dict[str, Any]:
    with open("config.json") as f:
        return json.load(f)


async def run_async(
    topic: str,
    hours: float,
    focus: str,
    progress_callback: Optional[Callable[[str, float], None]] = None,
    cancel_event: Optional[asyncio.Event] = None,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    config = config or load_config()
    db = DatabaseManager(config["database"]["path"])
    agent = ResearchAgent(config, db, progress_callback=progress_callback, cancel_event=cancel_event)
    try:
        return await agent.run_research(topic, hours, focus)
    finally:
        db.close()


def run(
    topic: str,
    hours: float,
    focus: str,
    progress_callback: Optional[Callable[[str, float], None]] = None,
    cancel_event: Optional[asyncio.Event] = None,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return asyncio.run(
        run_async(
            topic,
            hours,
            focus,
            progress_callback=progress_callback,
            cancel_event=cancel_event,
            config=config,
        )
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run research agent")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--hours", type=float, default=1)
    parser.add_argument("--focus", default="")
    args = parser.parse_args()
    run(args.topic, args.hours, args.focus)
