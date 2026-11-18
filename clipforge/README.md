# ClipForge: an AI-run video clipping agency

ClipForge is a business, not just a set of agents. Creators send long-form videos or podcasts,
a team of AI agents turns them into vertical short-form clips, and you (the CEO) approve every
clip before it ships. One dashboard shows every agent working, every video in production and
every finished clip waiting for approval.

```
                              YOU (CEO): dashboard, approvals, final say
                                               │
 GROWTH            PRODUCTION                    EDITING (ffmpeg)                     FILMCRAFT                       QC & DISTRIBUTION     BUSINESS
 research ► sales  intake ► strategist ► clipper ► pacing ► motion ► audio ► captioner ► assembler ► colorist ► finisher ► quality ► [you] ► publisher ► business
                                         9:16     jump     punch-   -14 LUFS captions,  .fcproj     Lumetri    FilmCraft  review   approve  platform   deliver,
                                         cut      cuts     ins      + music  .otio      project     look       render     clips             packages   invoice
                                           ▲                                                                                │
                                           └──────────────── re-cut / re-caption (automatic fixes, max 2 tries) ─────────────┘
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
| **pacing editor** | cut clips | Finds dead air with ffmpeg's silence detection and removes it with jump cuts, keeping a short breath around speech. | motion editor |
| **motion editor** | paced clips | Slow push-in under the hook, then 112% punch-ins on alternating sentences so the frame keeps moving. | audio engineer |
| **audio engineer** | zoomed clips | Masters to -14 LUFS (the TikTok/Reels/Shorts target). If the music library has tracks, it lays one under the voice and ducks it automatically whenever someone speaks. Each client always gets the same track. | captioner |
| **captioner** | edited clips | Burns 3-word captions re-timed to the jump cuts, highlights one keyword per caption, adds the hook (first 3s) and a progress bar, and exports `.srt` + `.otio` files. | quality |
| **quality** | captioned clips | Checks format, length, clean start, hook length, caption coverage and readability, loudness and pacing. Sends fixable problems back to the clipper or captioner. | you |
| **publisher** | clips you approved | Writes captions and hashtags for TikTok, Reels and Shorts and books the next free posting slot per platform. | business |
| **business** | finished orders, won leads | Marks orders delivered, issues invoices, flags overdue ones, and turns won leads into clients. | n/a |

| **assembler** (FilmCraft) | captioned clips | Builds a real FilmCraft project: a 1080x1920 sequence, the kept spans as cuts, a blurred fill on V1 behind the full frame on V2, keyframed push-in and punch-ins (Motion ▸ Scale, hold keyframes), a styled Captions track and a Hook track, and the music on A2 with Essential Sound auto-ducking and dialogue matched to -14 LUFS. | colorist |
| **colorist** (FilmCraft) | assembled clips | Picks a Lumetri look: the client's house look if set, otherwise Claude reads a rendered frame, otherwise a brightness/saturation heuristic. Grades every shot and saves a before/after still for your review. | finisher |
| **finisher** (FilmCraft) | graded clips | Renders the project with FilmCraft's engine (normalised to -14 LUFS), then burns ClipForge's styled captions, hook box and progress bar on top. | quality |

You can pause any agent from the dashboard. Pausing an editor **bypasses** it instead: clips keep
flowing, just without that pass. If an editing pass fails, the clip continues unedited and the error
shows on the dashboard. QC also checks loudness against the -14 LUFS target and checks caption
coverage against the edited timeline.

## The FilmCraft department

[FilmCraft](https://getartcraft.com/apps/filmcraft) is an open-source professional video editor
where every action is a command an agent can run. ClipForge's three FilmCraft agents drive its
headless engine (`filmcraft-cli run`) with the same commands its UI uses. So every clip ships with
`clip_N.fcproj`, a complete FilmCraft project you can open and change: cuts, keyframes, grade,
captions and mix. Download it from the approval card ("FilmCraft project").

```bash
# build FilmCraft's command-line tool (Rust 1.95+), or install a release (Linux: /usr/bin/filmcraft-cli)
git clone https://github.com/storytold/filmcraft && cd filmcraft
cargo build --release -p filmcraft-cli
export FILMCRAFT_CLI=$PWD/target/release/filmcraft-cli
```

Without `FILMCRAFT_CLI` (or `filmcraft-cli` on `PATH`), the FilmCraft agents skip themselves and the
ffmpeg render ships. If a FilmCraft pass fails, the clip continues with what it already has, and
the error shows on the dashboard. You can bypass any of the three from the dashboard.

**Speed:** FilmCraft renders on the CPU today (its README lists this as a known gap). On a 4-core
machine a 30-second vertical clip takes about 3-4 minutes. That runs in parallel with every other
agent, so it adds latency per clip, not a queue for the agency. Bypass the finisher to deliver the
faster ffmpeg render and still get the `.fcproj` project.

Set a client's **house look** in the "+ Client" dialog to grade all their clips the same way.

## Fine-tuning an edit in other editors

The captioner writes every clip's edit as an [OpenTimelineIO](https://opentimeline.io) timeline
(`data/output/clip_N.otio`, "Edit in FilmCraft (.otio)" on each approval card). It points at the
client's **original footage**, with one clip per kept span on V1/A1 and markers for the hook window,
each jump cut and each punch-in. So you, or a human editor you hire, can open the AI's cut in
[FilmCraft](https://getartcraft.com/apps/filmcraft) (File ▸ Import, or `filmcraft-cli import`) and adjust
everything instead of starting over. Import `clip_N.srt` alongside it for the captions.

In FilmCraft, set the sequence to 1080x1920 for vertical delivery; the 9:16 reframe and the zooms come
across as markers, not effects. Any OTIO-capable editor (DaVinci Resolve, Premiere via plugin)
can read the same file.

**Music:** add tracks you have the rights to with "+ Music track" on the dashboard, or drop them in `data/music/`. Clips flagged by the QC agent that fail twice go to
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
- **Speaker tracking**: reframing and punch-ins are centred. Face tracking (e.g. MediaPipe) would improve two-person podcasts.
- **Filler words** ("um", "uh"): removing them needs word-level timestamps. `faster-whisper` can provide them (`word_timestamps=True`); the edit-map plumbing for that already exists in `agency/editing.py`.
- **Live FilmCraft sessions**: the agents use FilmCraft headlessly. Its MCP bridge (`filmcraft --control`) would let you watch an agent edit inside the running app, or ask Claude to make changes there.

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
  editing.py    edit maps: remap transcript/caption timing through jump cuts
  handoff.py    OpenTimelineIO export for FilmCraft and other editors
  filmcraft.py  client for FilmCraft's headless engine (filmcraft-cli run/exec/inspect/export/render)
  orchestrator.py  runs all agents concurrently and recovers interrupted work on restart
  api.py        REST API + dashboard data
  static/       dashboard (plain HTML/CSS/JS, refreshes every 2s)
  db.py         SQLite: clients, leads, outreach, orders, clips, invoices, agents, events
  media.py      ffmpeg/ffprobe helpers
  transcript.py SRT/VTT/JSON parsing, optional Whisper transcription
scripts/demo.py seeds demo data (`--run` processes it without the server)
tests/          end-to-end pipeline tests (heuristic mode, real ffmpeg renders);
                FILMCRAFT_CLI=... pytest also runs the FilmCraft agents for real (slow)
```

Leads can be imported from CSV; see `leads_sample.csv` for the columns.
