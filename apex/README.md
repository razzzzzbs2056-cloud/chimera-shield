# ▲ Apex: Top 1% Life OS

Apex is a website and installable phone/desktop app that tracks every part of your day.
Each life area has its own tracker, and together they roll up into one **Life Score**
that ranks your day from *Just starting* up to **Top 1%**.

| Area | Trackers |
|------|----------|
| 💪 Body | 😴 Sleep · 🏋️ Fitness · 🥗 Nutrition |
| 🧠 Mind | 🧘 Mindset · 📚 Learning · 📵 Digital Discipline |
| 🎯 Work | 🎯 Deep Work (focus timer) · 🏔️ Goals |
| 💰 Wealth | 💰 Finance |
| ❤️ Life | ✅ Habits · 🤝 Relationships · 📝 Daily Review |

## Run it

No install and no build step are needed, just a static file server:

```bash
make apex            # from the repo root, then open http://localhost:5173
# or
cd apex && python3 -m http.server 5173
```

**Install as an app:** open the site on your phone and choose *Add to Home Screen* (iOS) or
*Install app* (Android/Chrome). It works fully offline.

## Test

```bash
node apex/tests/smoke.mjs          # every tracker, desktop + mobile, fails on any console error
node apex/tests/smoke.mjs sleep    # one tracker
```

## Docs

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): how the parts connect, and which agent built each part
- [`docs/MODULE_CONTRACT.md`](docs/MODULE_CONTRACT.md): how to write a new tracker

All data stays on your device. Back up with Settings → Export JSON.
