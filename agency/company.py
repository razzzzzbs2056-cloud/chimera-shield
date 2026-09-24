"""The org chart: a CEO agent that delegates to specialist sub-agents.

    CEO ──┬── Marketing  (strategy, campaigns; sees the whole board)
          ├── Content    (blog posts, social posts, scripts)
          ├── Email      (drafts and sends email)
          └── Engineer   (writes code: landing pages, scripts, integrations)

All agents share one Board, so marketing — and the CEO — see every campaign,
piece of content, email and code file the company has produced.
"""

from __future__ import annotations

from agency.agent import Agent
from agency.board import Board
from agency.config import Config
from agency.llm import LLM, make_llm
from agency.tools import Tool, schema
from agency.tools.email import Mailer
from agency.tools.workspace import Workspace

TEAM = {
    "marketing": (
        "Head of Marketing",
        "You own marketing strategy. Start by reading the board to see every campaign, "
        "piece of content and email so far, then define the audience, positioning, channels "
        "and schedule, and post the campaign plan to the board.",
    ),
    "content": (
        "Head of Content",
        "You write publish-ready content: blog posts, social posts, video scripts and "
        "newsletters. Read the board first so your work matches the current campaign, then "
        "publish each finished piece.",
    ),
    "email": (
        "Email Marketing Lead",
        "You write and send marketing email. Read the board for the campaign and content to "
        "promote. Keep emails short, honest and include a clear call to action. Only email "
        "recipients named in your task; never invent or scrape addresses.",
    ),
    "engineer": (
        "Lead Engineer",
        "You write working code for the company: landing pages, scripts, integrations. Write "
        "complete files to the workspace, and keep them small and self-contained.",
    ),
}

CEO_PROMPT = """You are the CEO of {company}, an AI content creation company.
Your team: {team}.
Turn the goal you are given into work for your team using the delegate tool — give each
sub-agent a specific, self-contained task. Delegate to marketing first so the campaign guides
everything else. When the team is done, read the board and reply with a short executive summary:
what was produced, what was sent, and recommended next steps."""


class Company:
    def __init__(self, config: Config | None = None, llm: LLM | None = None):
        self.config = config or Config()
        self.config.workspace.mkdir(parents=True, exist_ok=True)
        self.llm = llm or make_llm(self.config)
        self.board = Board(self.config.workspace / "board.json")
        self.workspace = Workspace(self.config.workspace)
        self.mailer = Mailer(self.config)
        self.team = {name: self._hire(name) for name in TEAM}
        self.ceo = Agent(
            "ceo",
            "CEO",
            CEO_PROMPT.format(
                company=self.config.company_name,
                team=", ".join(f"{n} ({TEAM[n][0]})" for n in TEAM),
            ),
            [self._delegate_tool(), self._view_board_tool()],
            self.llm,
            self.config.max_turns,
        )

    def run(self, goal: str) -> str:
        return self.ceo.run(goal)

    # --- hiring -----------------------------------------------------------

    def _hire(self, name: str) -> Agent:
        title, prompt = TEAM[name]
        tools = [self._view_board_tool()] + {
            "marketing": [self._campaign_tool()],
            "content": [self._content_tool()],
            "email": [self._email_tool()],
            "engineer": [self._write_file_tool()],
        }[name]
        system = f"You are the {title} at {self.config.company_name}. {prompt}"
        return Agent(name, title, system, tools, self.llm, self.config.max_turns)

    # --- tools --------------------------------------------------------------

    def _delegate_tool(self) -> Tool:
        def delegate(agent: str, task: str) -> str:
            report = self.team[agent].run(task)
            self.board.post("note", agent, f"Report to CEO: {task[:60]}", report)
            return report

        return Tool(
            "delegate",
            "Assign a task to a sub-agent and get back their report when they finish.",
            schema({
                "agent": {"type": "string", "enum": list(TEAM)},
                "task": {"type": "string", "description": "A specific, self-contained assignment."},
            }),
            delegate,
        )

    def _view_board_tool(self) -> Tool:
        return Tool(
            "view_board",
            "See everything the company has produced: campaigns, content, emails, code and reports.",
            schema({"kind": {"type": "string", "enum": ["campaign", "content", "email", "code", "note"]}}, required=[]),
            lambda kind=None: self.board.summary(kind),
        )

    def _campaign_tool(self) -> Tool:
        def post_campaign(title: str, audience: str, channels: list[str], plan: str) -> str:
            e = self.board.post("campaign", "marketing", title, plan, audience=audience, channels=channels)
            return f"Campaign #{e.id} posted."

        return Tool(
            "post_campaign",
            "Publish a marketing campaign plan to the board.",
            schema({
                "title": {"type": "string"},
                "audience": {"type": "string"},
                "channels": {"type": "array", "items": {"type": "string"}},
                "plan": {"type": "string", "description": "Positioning, messages, schedule and goals."},
            }),
            post_campaign,
        )

    def _content_tool(self) -> Tool:
        def publish_content(title: str, format: str, body: str) -> str:
            n = len(self.board.list("content")) + 1
            path = self.workspace.write(f"content/{n:03d}-{format}.md", body)
            e = self.board.post("content", "content", title, body, format=format, file=str(path))
            return f"Content #{e.id} saved to {path}."

        return Tool(
            "publish_content",
            "Save a finished piece of content (markdown) and post it to the board.",
            schema({
                "title": {"type": "string"},
                "format": {"type": "string", "enum": ["blog", "social", "video_script", "newsletter"]},
                "body": {"type": "string"},
            }),
            publish_content,
        )

    def _email_tool(self) -> Tool:
        def send_email(to: str, subject: str, body: str) -> str:
            status = self.mailer.send(to, subject, body)
            self.board.post("email", "email", subject, body, to=to, status=status.split(":")[0])
            return status

        return Tool(
            "send_email",
            "Send one email. Runs as a dry run (saved to the outbox) unless real sending is enabled.",
            schema({
                "to": {"type": "string", "description": "A single recipient email address."},
                "subject": {"type": "string"},
                "body": {"type": "string", "description": "Plain-text body."},
            }),
            send_email,
        )

    def _write_file_tool(self) -> Tool:
        def write_file(path: str, content: str) -> str:
            full = self.workspace.write(path, content)
            self.board.post("code", "engineer", path, content, file=str(full))
            return f"Wrote {len(content)} bytes to {full}."

        return Tool(
            "write_file",
            "Create or overwrite a file inside the company workspace.",
            schema({
                "path": {"type": "string", "description": "Relative path, e.g. site/index.html"},
                "content": {"type": "string"},
            }),
            write_file,
        )
