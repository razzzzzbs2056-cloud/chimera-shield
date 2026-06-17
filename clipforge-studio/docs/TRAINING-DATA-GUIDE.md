# Training data for an auto-editing AI — the practical guide

You asked what data you'd need to "train an AI" for an auto video editor. This
guide answers that honestly, in two parts:

1. **The short answer:** for almost everyone, *don't* train a model from
   scratch. Use heuristics + existing hosted AI models. ClipForge Studio already
   ships both (see [README](../README.md)).
2. **The long answer:** if you genuinely want to train your own model, here is
   exactly what data, labels, and pipeline you'd need — and roughly what it
   costs.

---

## 1. Why you probably shouldn't train your own model first

"Auto-editing" is not one model — it's a pipeline of sub-tasks, and **each
sub-task already has a strong off-the-shelf model or a cheap heuristic**:

| Editing sub-task | Don't train — use this instead |
|---|---|
| Find the spoken words | **Speech-to-text**: OpenAI Whisper (API or `whisper.cpp` / `transformers.js` locally) |
| Find "exciting" moments | **Audio loudness/energy heuristic** (ships in ClipForge, runs in-browser), or scene-change detection (PySceneDetect) |
| Pick the best clip / write a hook | **An LLM** (Claude) prompted with the transcript — ClipForge does this |
| Remove silence / filler words | Whisper word timestamps + a rule, or tools like `auto-editor` |
| Crop to a subject (reframe) | Pretrained face/person detection (MediaPipe, YOLO) — already trained |
| Add captions | Whisper output + render — no training |

Training a *new* model only makes sense when you have a task **none** of these
cover and you have a real labeled dataset. Until then, the fastest path to a
great product is orchestration, not training.

---

## 2. If you still want to train your own model

Pick the **one** sub-task you want to beat the market on. "Train an AI that edits
videos" end-to-end is a research-lab-scale problem; "train a model that predicts
which 15 seconds of a podcast will go viral" is a weekend-to-quarter project.

### 2a. Highlight / "best moment" detection (the most common goal)

**What the model learns:** given a video, output a score per second (or per
shot) for "how likely this moment is a highlight."

**Data you need:**

| Item | Detail |
|---|---|
| **Raw videos** | Hundreds to low-thousands of source videos in your niche (e.g. gaming, podcasts, fitness). Diversity matters more than raw count. |
| **The label** | For each video, the timestamp ranges humans actually clipped. Best source: **your own / creators' published shorts** matched back to the long-form original. Each (long video, short clip) pair gives you positive spans; everything else is negative. |
| **Engagement signal (optional, powerful)** | View-through / replays / likes per segment from analytics. Turns "a human clipped this" into "this clip *performed*." |
| **Derived features** | Per-second: audio loudness/RMS, speech vs music vs silence (from Whisper/VAD), scene-cut density, on-screen motion, sentiment of the transcript. These are your model inputs. |

**Rough scale:** a usable v1 highlight ranker needs on the order of **300–1,000
labeled videos** (tens of thousands of labeled seconds). Below that, a heuristic
will usually win.

**Labels format (example, one row per segment):**

```json
{ "video_id": "abc", "start": 142.0, "end": 156.5, "is_highlight": 1, "views": 48000, "loudness": 0.81, "speech": 1, "scene_cuts": 3 }
```

### 2b. Other trainable sub-tasks (and their data)

| Sub-task | Label you must collect |
|---|---|
| Filler-word / silence removal | Word-level transcript timestamps + human "keep/cut" decisions per word |
| Auto-reframe (subject tracking) | Per-frame bounding box of the subject (or use a pretrained detector and skip training) |
| Caption styling / emphasis | Transcripts annotated with which words to emphasize/animate |
| B-roll suggestion | (transcript span → chosen b-roll clip) pairs |

### 2c. The pipeline (once you have data)

```
collect videos
   └─ extract features (Whisper transcript + word timestamps, audio RMS,
      scene detection via PySceneDetect, motion/optical-flow, frame embeddings)
        └─ align labels (match published shorts back to source timestamps)
            └─ split train / val / test BY VIDEO (never leak segments of the
               same video across splits)
                └─ train a sequence model (start simple: gradient-boosted trees
                   or a small temporal CNN/transformer over per-second features)
                    └─ evaluate (precision@k of predicted highlights, IoU vs
                       human clips) → iterate
```

**Start simple.** A gradient-boosted tree (XGBoost/LightGBM) on per-second
features often gets you 80% of the value before any deep learning. Only reach for
a temporal transformer once the simple model plateaus and you have the data to
justify it.

### 2d. Tooling & cost reality

- **Feature extraction**: `ffmpeg`, `openai-whisper` / `faster-whisper`,
  `PySceneDetect`, `librosa`, `mediapipe`.
- **Training**: scikit-learn / XGBoost for the simple path; PyTorch for deep
  models.
- **Compute**: the simple path trains on a laptop. A deep temporal model wants a
  single GPU for hours, not a cluster.
- **The real cost is labeling, not GPUs.** Matching shorts to source videos and
  cleaning timestamps is the bulk of the work. Budget your time there.

### 2e. Legal / ethical checklist (do this first)

- You must have the **rights** to every training video (your own content,
  licensed, or explicitly permission-granted). Scraping other creators' videos
  to train a model is a licensing and ToS minefield.
- Strip or honor privacy for any identifiable people.
- Keep a provenance record of where each clip came from.

---

## 3. Recommended path for ClipForge Studio

1. **Ship the heuristic + hosted-AI version now** (already done): in-browser
   loudness highlight detection, Whisper transcription, Claude-written hooks.
2. **Instrument it**: log which suggested clips users actually keep, trim, and
   export. *That log is your future training set* — collected with consent, from
   your own product, perfectly labeled by user behavior.
3. **Only then** train a highlight ranker on that data to beat the heuristic.

This way you never block the product on a dataset you don't have yet, and the
dataset builds itself while users get value today.
