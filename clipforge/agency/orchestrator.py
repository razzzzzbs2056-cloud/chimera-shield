"""Runs every agent concurrently. Each agent takes one unit of work per tick, so a
slow render never blocks sales, research or QC."""
import asyncio
import logging

from . import config, db
from .agents import ALL

log = logging.getLogger("clipforge")


class Orchestrator:
    def __init__(self):
        db.init()
        # Anything left mid-flight by a crash/restart goes back to its queue.
        for table, busy, back in [("orders", "intake", "received"), ("orders", "planning", "transcribed"),
                                  ("clips", "cutting", "planned"), ("clips", "captioning", "cut"),
                                  ("clips", "qc", "captioned"), ("clips", "publishing", "approved")]:
            db.execute(f"UPDATE {table} SET status = ? WHERE status = ?", (back, busy))
        self.agents = [A() for A in ALL]
        for a in self.agents:
            a.idle()
        self._task: asyncio.Task | None = None
        self.running = False

    async def _run_agent(self, agent):
        while self.running:
            did = False
            if agent.enabled():
                did = await asyncio.to_thread(agent.tick)
            if not did:
                await asyncio.sleep(config.TICK_SECONDS)

    async def _main(self):
        await asyncio.gather(*(self._run_agent(a) for a in self.agents))

    def start(self):
        if not self.running:
            self.running = True
            self._task = asyncio.create_task(self._main())
            log.info("Orchestrator started with %d agents", len(self.agents))

    async def stop(self):
        self.running = False
        if self._task:
            await self._task

    def run_until_idle(self, max_rounds: int = 500) -> int:
        """Synchronous driver used by tests and the CLI demo."""
        rounds = 0
        while rounds < max_rounds:
            rounds += 1
            if not any(a.tick() for a in self.agents if a.enabled()):
                break
        return rounds
