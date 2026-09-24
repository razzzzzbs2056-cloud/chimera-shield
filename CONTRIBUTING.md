# Contributing

Thanks for helping out! This project is MIT-licensed and open to contributions.

1. Fork the repo and create a branch: `git checkout -b my-change`
2. Install: `make install`
3. Make your change. For the agent company, `make agency-demo` runs it offline.
4. Run the tests: `make test`
5. Open a pull request describing what changed and why.

Guidelines:
- Keep pull requests focused on one change.
- Add or update tests for behavior changes.
- Never commit secrets. Keep API keys and SMTP passwords in `.env` (it is git-ignored).
- New agent tools that act on the outside world (email, posting, payments) must be
  dry-run by default and opt-in to go live.
