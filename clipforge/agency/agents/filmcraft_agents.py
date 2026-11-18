"""The FilmCraft department: agents that edit inside FilmCraft, the open-source NLE.

    captioner -> [assembler] -> [colorist] -> [finisher] -> quality

They drive FilmCraft's headless engine with the same commands its UI uses, so every
clip gets a real `.fcproj` project you or a human editor can open and change:

- assembler: vertical 1080x1920 sequence, the kept spans as cuts, a blurred fill
  behind the full frame, keyframed push-in and punch-ins, caption and hook tracks,
  and the music bed on A2 with Essential Sound auto-ducking and -14 LUFS dialogue.
- colorist: picks a Lumetri look (client preference, Claude reading a frame, or a
  measured heuristic) and grades every shot.
- finisher: renders the project with FilmCraft's engine, then burns ClipForge's
  styled captions, hook box and progress bar on top.

Without FilmCraft (FILMCRAFT_CLI unset) they bypass, and the ffmpeg render ships.
"""
import base64
import json
import re
import subprocess
from pathlib import Path

from pydantic import BaseModel

from .. import config, db, filmcraft, llm, media
from .editors import EditorAgent, add_log, load_map, pick_track

T = filmcraft.TICKS
DEFAULT_LOOK = "Boost Vibrance"
LOOKS = {
    "Boost Vibrance": "more colour in the less saturated areas (safe for faces)",
    "Teal Shadows, Warm Skin": "cinematic teal/orange, a little more contrast",
    "Golden Dusk": "warm, soft late-afternoon light",
    "Warm Negative": "warm film print with gentle roll-off",
    "Faded Print": "lifted blacks, softer contrast, muted colour",
    "Steel Blue": "cool, desaturated and punchy",
    "Hard Sun": "high contrast, deep shadows",
    "Lift Shadows": "opens up dark footage",
    "Protect Highlights": "tames blown-out bright footage",
    "Neutral Mono": "black and white",
}
PUSH_IN, PUSH = 2.5, 1.06


def project_path(clip: dict) -> str:
    return str(Path(config.OUTPUT) / f"clip_{clip['id']}.fcproj")


def ticks(seconds: float) -> int:
    return int(round(seconds * T))


def zoom_at(t: float, zooms: list[list[float]]) -> float:
    if t < PUSH_IN:
        return 1 + (PUSH - 1) * t / PUSH_IN
    return next((z for a, b, z in zooms if a <= t < b), 1.0)


def zoom_keys(zooms: list[list[float]], fps: float) -> list[tuple[float, float, str]]:
    """(sequence time, zoom factor, interpolation) breakpoints for the foreground scale."""
    keys = [(0.0, 1.0, "linear"), (PUSH_IN - 1 / fps, PUSH, "hold"), (PUSH_IN, 1.0, "hold")]
    for a, b, z in zooms:
        keys += [(a, z, "hold"), (b, 1.0, "hold")]
    return sorted(keys)


def caption_srt_upper(srt: str, dst: Path) -> str:
    """FilmCraft caption tracks keep text as written: upper-case it to match the burned style."""
    out = []
    for line in Path(srt).read_text().splitlines():
        out.append(line if ("-->" in line or line.strip().isdigit() or not line.strip()) else line.upper())
    dst.write_text("\n".join(out) + "\n")
    return str(dst)


class FilmCraftAgent(EditorAgent):
    """An editor that works in FilmCraft; bypasses itself when FilmCraft isn't installed."""

    def step(self) -> bool:
        if not filmcraft.available():
            clip = db.claim("clips", self.takes, self.gives)
            if clip:
                self.log(f"Clip #{clip['id']}: skipped, FilmCraft not installed (set FILMCRAFT_CLI)", entity=("clip", clip["id"]))
            return bool(clip)
        return super().step()


class FilmCraftAssembler(FilmCraftAgent):
    name, role = "assembler", "Builds the edit in FilmCraft"
    takes, busy, gives = "captioned", "fc_assembling", "assembled"
    verb = "Assembling in FilmCraft"

    def edit(self, clip):
        cid = clip["id"]
        order = db.row("SELECT * FROM orders WHERE id = ?", (clip["order_id"],))
        em = load_map(clip)
        src = str(Path(order["source_path"]).resolve())
        info = media.probe(src)
        fps = 30.0
        proj = project_path(clip)
        Path(proj).unlink(missing_ok=True)
        music = pick_track(f"client-{order['client_id']}")
        srt = caption_srt_upper(clip["srt_path"], Path(config.WORK) / f"clip_{cid}_fc.srt") if clip.get("srt_path") else None

        # 1) sequence, media and caption track
        steps = [{"id": "file.newSequence", "params": {"name": f"Clip {cid}: {clip['hook']}", "width": config.OUT_W,
                                                        "height": config.OUT_H, "fps": fps, "video": 2, "audio": 2}},
                 {"id": "file.import", "params": {"paths": [src] + ([str(music.resolve())] if music else [])}}]
        if srt:
            steps.append({"id": "captions.import", "params": {"path": srt, "name": "Captions"}})
        steps.append({"id": "captions.newTrack", "params": {"format": "Subtitle", "name": "Hook"}})
        res = filmcraft.run(steps, save_as=proj)
        items = res[1]["items"]
        hook_track = res[-1]["track"]
        cap_track = next((t["id"] for t in filmcraft.run([{"id": "captions.list", "params": {}}], project=proj)[0]["tracks"]
                          if t["id"] != hook_track), None)
        src_item, music_item = items[0], (items[1] if music and len(items) > 1 else None)

        # 2) cuts: blurred fill on V1 (picture only), full frame on V2 with its sound on A1
        steps, t = [], 0.0
        for a, b in em["keeps"]:
            span = {"seconds": t, "sourceIn": {"seconds": clip["start"] + a}, "duration": {"seconds": b - a}}
            steps.append({"id": "timeline.place", "params": {"item": src_item, "track": "V1", "audio": False, **span}})
            steps.append({"id": "timeline.place", "params": {"item": src_item, "track": "V2", "audioTrack": "A1", **span}})
            t += b - a
        total = t
        if music_item:
            mdur = media.duration(music)
            m = 0.0
            while m < total - 0.05:
                d = min(mdur, total - m)
                steps.append({"id": "timeline.place", "params": {"item": music_item, "track": "A2", "seconds": m,
                                                                  "duration": {"seconds": d}}})
                m += d
        placed = filmcraft.run(steps, project=proj, save=True)
        bg = [r["clips"][0] for r in placed[0:2 * len(em["keeps"]):2]]
        fg = [r["clips"][0] for r in placed[1:2 * len(em["keeps"]):2]]
        dialog = [r["clips"][1] for r in placed[1:2 * len(em["keeps"]):2] if len(r["clips"]) > 1]
        music_clips = [c for r in placed[2 * len(em["keeps"]):] for c in r["clips"]]

        seq = filmcraft.inspect(proj)["sequence"]
        fg_items = {it["clip"]: it for it in seq["video"][1]["items"]}

        # 3) reframe, motion keyframes, captions, sound
        fill = max(config.OUT_W / info["width"], config.OUT_H / info["height"]) * 100
        fit = config.OUT_W / info["width"] * 100
        steps = [{"id": "effects.setParam", "params": {"clip": c, "effect": "motion", "param": "scale", "value": round(fill, 3)}} for c in bg]
        steps.append({"id": "effects.apply", "params": {"clips": bg, "effect": "gaussian_blur"}})
        steps += [{"id": "effects.setParam", "params": {"clip": c, "effect": "gaussian_blur", "param": "blurriness", "value": 60}} for c in bg]
        steps += [{"id": "effects.setParam", "params": {"clip": c, "effect": "gaussian_blur", "param": "repeat_edge", "value": True}} for c in bg]
        keys = zoom_keys(em["zooms"], fps)
        n_keys = 0
        for c in fg:
            it = fg_items[c]
            cs, ce = it["start"] / T, it["end"] / T
            pts = [(cs, zoom_at(cs, em["zooms"]), "linear" if cs < PUSH_IN else "hold")]
            pts += [k for k in keys if cs < k[0] < ce]
            for when, z, interp in pts:
                steps.append({"id": "effects.setParam", "params": {"clip": c, "effect": "motion", "param": "scale",
                                                                    "value": round(fit * z, 3), "keyframe": True, "time": ticks(when)}})
                if interp == "hold":
                    steps.append({"id": "effects.setInterpolation", "params": {
                        "clip": c, "effect": "motion", "param": "scale", "interpolation": "hold",
                        "mediaTime": it["sourceIn"] + ticks(when) - it["start"]}})
                n_keys += 1
        if cap_track is not None:  # sizes are pixels at 1080 lines, scaled to the frame
            steps.append({"id": "captions.setStyle", "params": {"track": cap_track, "font": "Inter", "fontStyle": "Bold", "size": 48,
                                                                 "color": "#FFFFFF", "background": False, "outline": 4, "outlineColor": "#000000",
                                                                 "align": "center", "anchor": "bottom", "margin": 0.29}})
        steps += [
            {"id": "captions.add", "params": {"track": hook_track, "text": clip["hook"].upper(), "seconds": 0, "durationSeconds": 3}},
            {"id": "captions.setStyle", "params": {"track": hook_track, "font": "Inter", "fontStyle": "Bold", "size": 38,
                                                    "color": "#000000", "background": True, "backgroundColor": "#FFE500FF",
                                                    "align": "center", "anchor": "top", "margin": 0.125}},
        ]
        if dialog:
            steps += [{"id": "essentialSound.setType", "params": {"clips": dialog, "type": "dialogue"}},
                      {"id": "essentialSound.autoMatch", "params": {"clips": dialog, "target": -14}}]
        if music_clips:
            steps += [{"id": "essentialSound.setType", "params": {"clips": music_clips, "type": "music"}},
                      {"id": "clip.audioGain", "params": {"clips": music_clips, "mode": "set", "db": -18}},
                      {"id": "essentialSound.generateDucking", "params": {"clips": music_clips}}]
        filmcraft.run(steps, project=proj, save=True)

        em["filmcraft"] = {"project": proj, "bg": bg, "fg": fg, "dialog": dialog, "music": music_clips}
        line = (f"assembler: FilmCraft project with {len(fg)} cut{'s' * (len(fg) != 1)}, blurred fill, "
                f"{n_keys} scale keyframes, caption + hook tracks"
                + (", music auto-ducked" if music_clips else ""))
        db.update("clips", cid, status=self.gives, edit_map=em, edit_log=add_log(clip, line))
        self.log(f"Clip #{cid}: built {Path(proj).name} ({line.split(': ', 1)[1]})", entity=("clip", cid))


class LookChoice(BaseModel):
    look: str
    reason: str


def frame_stats(png: str) -> dict:
    p = subprocess.run(["ffmpeg", "-i", png, "-vf", "signalstats,metadata=print", "-f", "null", "-"],
                       capture_output=True, text=True, timeout=60)
    get = lambda k: float(m.group(1)) if (m := re.search(rf"lavfi\.signalstats\.{k}=([\d.]+)", p.stderr)) else None
    return {"luma": get("YAVG"), "sat": get("SATAVG")}


def heuristic_look(stats: dict) -> tuple[str, str]:
    y, s = stats.get("luma"), stats.get("sat")
    if y is not None and y < 70:
        return "Lift Shadows", f"dark footage (average luma {y:.0f})"
    if y is not None and y > 190:
        return "Protect Highlights", f"bright footage (average luma {y:.0f})"
    if s is not None and s > 60:
        return "Teal Shadows, Warm Skin", "already colourful: add contrast and separation"
    return DEFAULT_LOOK, "safe default for talking-head footage"


class FilmCraftColorist(FilmCraftAgent):
    name, role = "colorist", "Grades the look in FilmCraft"
    takes, busy, gives = "assembled", "grading", "graded"
    verb = "Grading"

    def edit(self, clip):
        cid = clip["id"]
        em = load_map(clip)
        fc = em.get("filmcraft") or {}
        proj = fc.get("project")
        if not proj or not Path(proj).exists():
            raise RuntimeError("no FilmCraft project to grade")
        order = db.row("SELECT * FROM orders WHERE id = ?", (clip["order_id"],))
        client = db.row("SELECT * FROM clients WHERE id = ?", (order["client_id"],)) or {}
        before = str(Path(config.WORK) / f"clip_{cid}_ungraded.png")
        filmcraft.render_frame(proj, 4.0, before, scale=0.5)

        look, why = (client.get("look"), "client's house look") if client.get("look") in LOOKS else (None, "")
        if not look and llm.enabled():
            img = base64.standard_b64encode(Path(before).read_bytes()).decode()
            ai = llm.structured(
                "You are a colourist for short-form social video. Choose ONE look for this shot from the list. "
                "Faces must stay natural; prefer subtle looks unless the brief asks for style.",
                [{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img}},
                 {"type": "text", "text": f"Looks: {json.dumps(LOOKS)}\nClient: {client.get('name')}\nBrief: {order.get('brief')}"}],
                LookChoice, effort="low")
            if ai and ai.look in LOOKS:
                look, why = ai.look, ai.reason
        if not look:
            look, why = heuristic_look(frame_stats(before))

        filmcraft.run([{"id": "lumetri.applyPreset", "params": {"name": look, "clips": fc["fg"] + fc["bg"]}}],
                      project=proj, save=True)
        after = Path(config.OUTPUT) / f"clip_{cid}_graded.jpg"
        tmp = str(Path(config.WORK) / f"clip_{cid}_graded.png")
        filmcraft.render_frame(proj, 4.0, tmp, scale=0.5)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", before, "-i", tmp, "-filter_complex",
                        "[0][1]hstack=2,scale=540:-2", str(after)], check=True)
        em["look"] = look
        line = f"colorist: '{look}' ({why})"
        db.update("clips", cid, status=self.gives, edit_map=em, edit_log=add_log(clip, line))
        self.log(f"Clip #{cid}: graded '{look}' ({why})", entity=("clip", cid))


class FilmCraftFinisher(FilmCraftAgent):
    name, role = "finisher", "Renders the FilmCraft master"
    takes, busy, gives = "graded", "fc_rendering", "finished"
    verb = "Rendering"

    def edit(self, clip):
        cid = clip["id"]
        em = load_map(clip)
        proj = (em.get("filmcraft") or {}).get("project")
        if not proj or not Path(proj).exists():
            raise RuntimeError("no FilmCraft project to render")
        master = str(Path(config.WORK) / f"clip_{cid}_filmcraft.mp4")
        # FilmCraft renders picture and sound; caption tracks stay editable in the project
        # and ClipForge burns its own styled captions, hook box and progress bar on top.
        filmcraft.run([{"id": "file.exportMedia", "params": {
            "path": master, "format": "h264", "width": config.OUT_W, "height": config.OUT_H, "fps": 30,
            "bitrateMode": "crf", "crf": 18, "burnCaptions": False, "loudnessLufs": -14, "range": "entire", "wait": True}}],
            project=proj, timeout=3600)
        ass = Path(config.WORK) / f"clip_{cid}.ass"
        final = Path(config.OUTPUT) / f"clip_{cid}.mp4"
        dur = media.probe(master)["duration"]
        media.burn_subtitles(master, str(ass), str(final), duration=dur)
        media.thumbnail(str(final), str(Path(config.OUTPUT) / f"clip_{cid}.jpg"), at=1.0)
        lufs = media.integrated_loudness(str(final))
        line = f"finisher: rendered by FilmCraft ({dur:.1f}s" + (f", {lufs:.1f} LUFS)" if lufs is not None else ")")
        db.update("clips", cid, status=self.gives, final_path=str(final), edit_log=add_log(clip, line))
        self.log(f"Clip #{cid}: {line.split(': ', 1)[1]}", entity=("clip", cid))
