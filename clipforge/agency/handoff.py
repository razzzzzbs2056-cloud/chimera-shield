"""Editor handoff: write each clip's AI edit as an OpenTimelineIO timeline.

The .otio file points at the client's ORIGINAL footage, with one clip per kept
span, so a human editor can open the AI's cut in FilmCraft (File > Import), or any
other OTIO-capable editor, and adjust every cut, punch-in and caption. Markers show
the hook window, each jump cut and each punch-in; captions ship as a matching .srt."""
import json
from pathlib import Path

from . import config, editing


def _rt(seconds: float, rate: float) -> dict:
    return {"OTIO_SCHEMA": "RationalTime.1", "rate": rate, "value": round(seconds * rate)}


def _tr(start: float, dur: float, rate: float) -> dict:
    return {"OTIO_SCHEMA": "TimeRange.1", "start_time": _rt(start, rate), "duration": _rt(dur, rate)}


def _marker(name: str, start: float, dur: float, rate: float, color: str, comment: str = "") -> dict:
    return {"OTIO_SCHEMA": "Marker.2", "name": name, "marked_range": _tr(start, dur, rate),
            "color": color, "comment": comment, "metadata": {}}


def build_otio(clip: dict, order: dict, edit_map: dict, source_info: dict, srt_name: str | None = None) -> dict:
    rate = source_info.get("fps") or 30.0
    src = Path(order["source_path"]).resolve()
    ref = {"OTIO_SCHEMA": "ExternalReference.1", "name": src.name, "target_url": src.as_uri(),
           "available_range": _tr(0, source_info["duration"], rate), "available_image_bounds": None, "metadata": {}}
    keeps = edit_map.get("keeps") or editing.identity(clip["end"] - clip["start"])

    def track(kind: str) -> dict:
        children = []
        for i, (a, b) in enumerate(keeps, 1):
            children.append({
                "OTIO_SCHEMA": "Clip.2", "name": f"{src.stem} [{i}]",
                "source_range": _tr(clip["start"] + a, b - a, rate),
                "effects": [], "markers": [], "enabled": True,
                "media_references": {"DEFAULT_MEDIA": ref}, "active_media_reference_key": "DEFAULT_MEDIA",
                "metadata": {},
            })
        return {"OTIO_SCHEMA": "Track.1", "name": "V1" if kind == "Video" else "A1", "kind": kind,
                "source_range": None, "children": children, "effects": [], "markers": [], "enabled": True,
                "metadata": {}}

    markers = [_marker(f"HOOK: {clip['hook']}", 0, 3.0, rate, "YELLOW", "On-screen hook text")]
    t = 0.0
    for a, b in keeps[:-1]:
        t += b - a
        markers.append(_marker("Jump cut", t, 1 / rate, rate, "RED", "Silence removed by the pacing editor"))
    for a, b, z in edit_map.get("zooms", []):
        markers.append(_marker(f"Punch-in {round(z * 100)}%", a, b - a, rate, "PURPLE", "Scale up, centred"))

    return {
        "OTIO_SCHEMA": "Timeline.1",
        "name": f"Clip {clip['id']}: {clip['hook']}",
        "global_start_time": _rt(0, rate),
        "metadata": {"clipforge": {
            "clip_id": clip["id"], "order_id": clip["order_id"], "hook": clip["hook"], "title": clip["title"],
            "delivery": {"width": config.OUT_W, "height": config.OUT_H,
                         "reframe": "vertical 9:16: full frame centred over a blurred, zoomed copy"},
            "edit_map": edit_map, "captions": srt_name,
        }},
        "tracks": {"OTIO_SCHEMA": "Stack.1", "name": "tracks", "children": [track("Video"), track("Audio")],
                   "effects": [], "markers": markers, "enabled": True, "source_range": None, "metadata": {}},
    }


def write_otio(clip: dict, order: dict, edit_map: dict, source_info: dict, srt_path: str | None) -> str:
    out = Path(config.OUTPUT) / f"clip_{clip['id']}.otio"
    out.write_text(json.dumps(build_otio(clip, order, edit_map, source_info,
                                         Path(srt_path).name if srt_path else None), indent=2))
    return str(out)
