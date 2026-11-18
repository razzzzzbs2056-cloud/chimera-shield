# ClipForge: an AI-run video clipping agency

ClipForge is a business, not just a set of agents. Creators send long-form videos or podcasts,
a team of AI agents turns them into vertical short-form clips, and you (the CEO) approve every
clip before it ships. One dashboard shows every agent working, every video in production and
every finished clip waiting for approval.

```
                        YOU (CEO): dashboard, approvals, final say
                                         │
   GROWTH                 PRODUCTION                               QC & DISTRIBUTION      BUSINESS
   research ─► sales      intake ─► strategist ─► clipper ─► captioner ─► quality ─► [you] ─► publisher ─► business
   find and     outreach   footage +   best         cut +       subtitles    review    approve   TikTok/Reels/  deliver,
   score leads  drafts     transcript  moments      9:16 crop   + hook       clips               Shorts pkgs    invoice
                                                       ▲             ▲           │
                                                       └── re-cut ───┴─ re-caption (automatic fixes, max 2 tries)
```

## Run it

```bash
make clipforge-install     # needs ffmpeg on PATH
make clipforge-demo        # optional: sample client, 2-min podcast video and 3 leads
make clipforge             # dashboard at http://localhost:8100
```

Within about a minute of running the demo you'll see 3 clips waiting for approval.

## What each agent does

| Agent | Picks up | Does | Hands off to |
|---|---|---|---|
| **research** | new leads | Scores fit 0-100 (audience size, upload cadence, no shorts yet, niche) and qualifies or drops them. With `YOUTUBE_API_KEY`, discovers real channels by keyword. | sales |
| **sales** | qualified leads, stale contacted leads | Drafts a personal first email, then up to 2 follow-ups 3 days apart. **Never sends anything**: drafts wait for you to edit, send and click "I sent it". | you |
| **intake** | uploaded orders | Checks the video (readable, long enough, has audio), loads the transcript (SRT/VTT/JSON) or transcribes with faster-whisper. | strategist |
| **strategist** | transcribed orders | Picks non-overlapping 15-60s moments with a hook up front, one idea and a payoff, plus the client's brief. Writes a hook for each. | clipper |
| **clipper** | planned clips | Cuts and reframes to 1080x1920 (full frame over a blurred fill, so nothing gets cropped off). | captioner |
| **captioner** | cut clips | Burns 3-word captions and the hook (first 3s), and exports an `.srt` file. | quality |
| **quality** | captioned clips | Checks format, length, clean start, hook length, caption coverage and readability, loudness and pacing. Sends fixable problems back to the clipper or captioner. | you |
| **publisher** | clips you approved | Writes captions and hashtags for TikTok, Reels and Shorts and books the next free posting slot per platform. | business |
| **business** | finished orders, won leads | Marks orders delivered, issues invoices, flags overdue ones, and turns won leads into clients. | n/a |

You can pause any agent from the dashboard. Clips flagged by the QC agent that fail twice go to
"Stopped", and you can still approve them by hand.

## AI vs. heuristic mode

With `ANTHROPIC_API_KEY` set, Claude (`claude-opus-5-5` by default, `CLIPFORGE_MODEL` to change)
does the judgement work: lead scoring, cold emails, moment selection, hooks, an editor-style QC
review and social captions. Each call returns structured output and falls back to the built-in
heuristic if it fails, so the line never stops. Without a key, everything runs on heuristics.
The dashboard header shows which mode is active.

## What isn't automated yet (on purpose)

- **Sending email**: drafts only. Wire SMTP or Gmail into `outreach_action` in `agency/api.py` when you trust the copy.
- **Posting to platforms**: TikTok, Instagram and YouTube uploads need approved developer apps and OAuth per client.
  The publisher writes a complete package (`data/output/clip_N_publish.json` + video + SRT); upload code goes in `agents/publisher.py`.
- **Payments**: invoices are tracked and marked paid by hand. A Stripe Payment Link per invoice is the natural next step.
- **Speaker tracking**: reframing centres the frame. Face tracking (e.g. MediaPipe) would improve two-person podcasts.

## Pricing (edit `PACKAGES` in `agency/config.py`)

| Package | Clips per video | Price |
|---|---|---|
| starter | 3 | $99 |
| growth | 6 | $179 |
| pro | 10 | $279 |

## Layout

```
agency/
  agents/       one file per agent (base.py has the shared status/logging loop)
  orchestrator.py  runs all agents concurrently and recovers interrupted work on restart
  api.py        REST API + dashboard data
  static/       dashboard (plain HTML/CSS/JS, refreshes every 2s)
  db.py         SQLite: clients, leads, outreach, orders, clips, invoices, agents, events
  media.py      ffmpeg/ffprobe helpers
  transcript.py SRT/VTT/JSON parsing, optional Whisper transcription
scripts/demo.py seeds demo data (`--run` processes it without the server)
tests/          end-to-end pipeline test (heuristic mode, real ffmpeg renders)
```

Leads can be imported from CSV; see `leads_sample.csv` for the columns.
