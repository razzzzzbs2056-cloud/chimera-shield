import logging
import traceback

from .. import db

logger = logging.getLogger("clipforge")


class Agent:
    """An agent pulls one unit of work per tick from the shared database.

    Subclasses implement `step()` returning True if they did work. Status and every
    action are written to the `agents` and `events` tables so the dashboard can show
    what each agent is doing in real time."""

    name = "agent"
    role = ""

    def __init__(self):
        if not db.row("SELECT name FROM agents WHERE name = ?", (self.name,)):
            db.execute("INSERT INTO agents (name, role, status, updated_at) VALUES (?, ?, 'idle', ?)",
                       (self.name, self.role, db.now()))

    # -- status helpers -------------------------------------------------
    def working(self, task: str):
        db.update("agents", self.name, key="name", status="working", current_task=task, updated_at=db.now())

    def idle(self):
        db.update("agents", self.name, key="name", status="idle" if self.enabled() else "paused",
                  current_task=None, updated_at=db.now())

    def enabled(self) -> bool:
        r = db.row("SELECT enabled FROM agents WHERE name = ?", (self.name,))
        return bool(r and r["enabled"])

    def log(self, msg: str, level: str = "info", entity: tuple[str, int] | None = None):
        et, eid = entity if entity else (None, None)
        db.log(self.name, msg, level, et, eid)
        logger.info("[%s] %s", self.name, msg)

    def done(self):
        db.execute("UPDATE agents SET processed = processed + 1 WHERE name = ?", (self.name,))

    # -- run loop entry -------------------------------------------------
    def tick(self) -> bool:
        try:
            did = self.step()
        except Exception as e:  # never let one bad job kill the agency
            db.execute("UPDATE agents SET errors = errors + 1 WHERE name = ?", (self.name,))
            self.log(f"Error: {e}", "error")
            logger.debug(traceback.format_exc())
            did = True
        finally:
            self.idle()
        return did

    def step(self) -> bool:  # pragma: no cover
        raise NotImplementedError
