"""Command line: python -m agency "Launch our AI newsletter service" [--mock]"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

from agency.config import Config


def main() -> None:
    parser = argparse.ArgumentParser(prog="agency", description="Run the AI content company on a goal.")
    parser.add_argument("goal", help="What the CEO should get done.")
    parser.add_argument("--mock", action="store_true", help="Run offline with scripted agents (no API key).")
    parser.add_argument("--workspace", type=Path, help="Where output is written (default: agency_output).")
    parser.add_argument("--send-emails", action="store_true", help="Actually deliver email via SMTP.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Only print the CEO's final summary.")
    args = parser.parse_args()

    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    logging.basicConfig(level=logging.WARNING if args.quiet else logging.INFO, format="%(message)s")
    config = Config()
    if args.mock:
        config.mock = True
    if args.workspace:
        config.workspace = args.workspace
    if args.send_emails:
        config.send_emails = True
    if not config.mock and not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")):
        parser.exit(1, "No ANTHROPIC_API_KEY set. Add one to .env, or try --mock.\n")

    from agency.company import Company

    company = Company(config)
    summary = company.run(args.goal)
    print("\n" + "=" * 60 + "\nCEO SUMMARY\n" + "=" * 60 + f"\n{summary}\n")
    print(f"Board, content, code and outbox: {config.workspace.resolve()}")


if __name__ == "__main__":
    main()
