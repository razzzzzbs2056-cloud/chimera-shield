import pytest

from agency import Company, Config
from agency.board import Board
from agency.tools.email import EmailError, Mailer
from agency.tools.workspace import Workspace


def make_config(tmp_path, **overrides) -> Config:
    config = Config()
    config.mock = True
    config.workspace = tmp_path
    config.send_emails = False
    for key, value in overrides.items():
        setattr(config, key, value)
    return config


def test_ceo_delegates_to_every_department(tmp_path):
    company = Company(make_config(tmp_path))
    company.run("Launch our AI newsletter service")

    kinds = {e.kind for e in company.board.list()}
    assert {"campaign", "content", "email", "code", "note"} <= kinds
    reporters = {e.author for e in company.board.list("note")}
    assert reporters == {"marketing", "content", "email", "engineer"}
    assert (tmp_path / "site" / "index.html").exists()
    assert list((tmp_path / "outbox").glob("*.eml"))


def test_board_is_shared_and_persisted(tmp_path):
    company = Company(make_config(tmp_path))
    company.run("Launch")
    reloaded = Board(tmp_path / "board.json")
    assert len(reloaded.list()) == len(company.board.list())
    # marketing sees what content and email produced
    view = company.team["marketing"].tools["view_board"].handler()
    assert "Launch blog post" in view and "is live" in view


def test_email_is_dry_run_by_default(tmp_path):
    status = Mailer(make_config(tmp_path)).send("a@example.com", "Hi", "Body")
    assert status.startswith("DRY RUN")


def test_email_guard_rails(tmp_path):
    mailer = Mailer(make_config(tmp_path, email_allowlist=["@ok.com"], max_emails_per_run=1))
    with pytest.raises(EmailError):
        mailer.send("not-an-address", "Hi", "Body")
    with pytest.raises(EmailError):
        mailer.send("a@blocked.com", "Hi", "Body")
    mailer.send("a@ok.com", "Hi", "Body")
    with pytest.raises(EmailError):
        mailer.send("b@ok.com", "Hi", "Body")


def test_workspace_blocks_path_escape(tmp_path):
    with pytest.raises(ValueError):
        Workspace(tmp_path).write("../evil.txt", "x")


def test_tool_errors_are_reported_to_the_model(tmp_path):
    company = Company(make_config(tmp_path))
    result = company.team["engineer"]._call(
        {"type": "tool_use", "id": "t1", "name": "write_file", "input": {"path": "../x", "content": ""}}
    )
    assert result["is_error"] and "escapes" in result["content"]
