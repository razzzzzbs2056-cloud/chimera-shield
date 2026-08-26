"""
Change-detection engine (interface + orchestration contract).

Pixel-level change detection (cloud masking -> registration -> terrain
correction -> normalisation -> differencing) is a heavy, GDAL/rasterio-bound
workload that belongs in a Celery worker operating on downloaded scene assets.
This module defines the contract and the *selection* logic that does not need
raster access, so the rest of the platform can depend on stable types.

Scientific rules encoded in the contract:
  * Optical change is only valid on cloud-free pixels; cloudy pixels are masked
    and never reported as confirmed surface change.
  * A SAR intensity change is an *observation to be validated*, not ground
    movement, unless InSAR processing + validation supports it.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class ChangeRequest:
    glacier_id: str
    before_scene_id: str
    after_scene_id: str
    modality: str  # "optical" | "sar"


@dataclass
class ChangePair:
    """The chosen before/after scenes for a comparison."""

    before_scene_id: str
    before_time: Optional[datetime]
    after_scene_id: str
    after_time: Optional[datetime]
    modality: str
    valid_for_change: bool
    reason: Optional[str] = None


def choose_comparable(scenes: List[dict], modality: str) -> Optional[ChangePair]:
    """Given scenes sorted newest-first (as connectors return), pick the newest
    and its closest comparable prior scene. For optical, require both scenes to
    be cloud-usable; otherwise the pair is flagged not valid for change."""
    usable = scenes
    if modality == "optical":
        usable = [s for s in scenes if s.get("cloud_usable")]
    if len(usable) < 2:
        # We may still have 2 scenes but they're cloudy -> report invalidity.
        if len(scenes) >= 2:
            a, b = scenes[0], scenes[1]
            return ChangePair(
                b.get("scene_id"), _t(b), a.get("scene_id"), _t(a), modality,
                valid_for_change=False,
                reason="insufficient cloud-free optical coverage for valid change",
            )
        return None
    after, before = usable[0], usable[1]
    return ChangePair(
        before.get("scene_id"), _t(before),
        after.get("scene_id"), _t(after), modality,
        valid_for_change=True,
        reason=None,
    )


def _t(scene: dict) -> Optional[datetime]:
    v = scene.get("acquisition_time")
    if not v:
        return None
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except ValueError:
        return None
