"""Seed the agency with a sample client, order and leads so you can watch the
whole pipeline run. Generates a synthetic 3-minute "podcast" video with ffmpeg.

    python -m scripts.demo            # seed only (agents run inside the server)
    python -m scripts.demo --run      # seed and process everything right here
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agency import config, db  # noqa: E402

LINES = [
    "Welcome back to the show. Today we're talking about how small businesses actually grow.",
    "Here's the biggest mistake I see founders make in their first year.",
    "They spend months building a product nobody asked for, and then wonder why it doesn't sell.",
    "I did exactly that. I lost about forty thousand dollars on my first company.",
    "So what changed? I started talking to ten customers every single week.",
    "Not surveys. Real conversations. You learn more in one call than in a hundred forms.",
    "And the second thing was pricing. Most people charge way too little.",
    "Why do you think that is?",
    "Honestly, fear. People are scared that if they raise prices, everyone will leave.",
    "But when we doubled our prices, we lost two clients and gained a lot more respect.",
    "That's crazy. Doubled, and you only lost two?",
    "Two. And those two were the ones causing ninety percent of our support tickets.",
    "Let's switch gears. Everyone asks me about social media.",
    "Here's the truth nobody tells you: you don't need to go viral.",
    "You need to show up consistently for the hundred people who might buy from you.",
    "Short clips from long conversations like this one are perfect for that.",
    "One episode can become ten pieces of content without any extra filming.",
    "What's the one habit that changed your business the most?",
    "Writing down every decision and why I made it. Every single one.",
    "Six months later you look back and realize which instincts were right and which were wrong.",
    "It sounds boring, but it is the most underrated tool for founders.",
    "Okay, last question. What would you tell someone starting today?",
    "Start smaller than you think. Charge more than you're comfortable with.",
    "And never stop talking to your customers. That's it. That's the whole secret.",
    "Amazing. Thanks so much for coming on the show.",
    "Thanks for having me. This was a lot of fun.",
]

LEADS = [
    dict(name="Maya Chen", email="maya@example.com", channel_url="https://www.youtube.com/@example-maya",
         platform="youtube", niche="business", followers=84000, avg_views=12000, uploads_per_week=1, has_shorts=0,
         notes="Weekly founder interviews, 60-90 min episodes"),
    dict(name="Tom Okafor", email="tom@example.com", platform="podcast", niche="fitness", followers=31000,
         avg_views=4000, uploads_per_week=2, has_shorts=1, notes="Fitness podcast with video"),
    dict(name="Lena Ruiz", platform="youtube", niche="gaming", followers=2500, avg_views=150,
         uploads_per_week=0.5, has_shorts=1, notes="Occasional streams"),
]


def make_video(path: Path, transcript_path: Path, seg_len: float = 6.5) -> None:
    segs, t = [], 0.0
    for line in LINES:
        n = len(line.split())
        dur = max(2.5, min(seg_len, n / 2.6))
        segs.append({"start": round(t, 2), "end": round(t + dur, 2), "text": line})
        t += dur + 0.3
    transcript_path.write_text(json.dumps(segs, indent=1))
    total = t + 1
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", f"testsrc2=size=1920x1080:rate=30:duration={total:.1f}",
        "-f", "lavfi", "-i", f"sine=frequency=220:sample_rate=48000:duration={total:.1f}",
        "-af", "volume=0.3", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-shortest", str(path)], check=True, capture_output=True)


def seed() -> int:
    db.init()
    video = config.UPLOADS / "demo_podcast.mp4"
    tr = config.UPLOADS / "demo_podcast_transcript.json"
    if not video.exists():
        print("Rendering demo video with ffmpeg...")
        make_video(video, tr)
    client = db.row("SELECT id FROM clients WHERE name = 'Founders Unfiltered'")
    cid = client["id"] if client else db.insert("clients", name="Founders Unfiltered", email="team@example.com",
                                               package="starter", status="active")
    n, price = config.PACKAGES["starter"]
    oid = db.insert("orders", client_id=cid, title="Ep. 12: Pricing, fear and talking to customers",
                    brief="Focus on pricing and founder mistakes", source_path=str(video),
                    transcript_path=str(tr), clips_requested=n, price_cents=price, status="received")
    db.log("intake", f"Order #{oid} received (demo)", entity_type="order", entity_id=oid)
    for l in LEADS:
        if not db.row("SELECT id FROM leads WHERE name = ?", (l["name"],)):
            db.insert("leads", **l, stage="new", updated_at=db.now())
    print(f"Seeded client #{cid}, order #{oid} and {len(LEADS)} leads.")
    return oid


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="process the pipeline now, without the server")
    args = ap.parse_args()
    seed()
    if args.run:
        from agency.orchestrator import Orchestrator
        Orchestrator().run_until_idle()
        for c in db.rows("SELECT id, status, hook, qc_score FROM clips ORDER BY id"):
            print(c)
