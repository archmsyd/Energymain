from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from floorplan_platform.models import Plan, empty_plan


def cubicasa_infer(image_path: Path) -> Dict[str, Path]:
    """Run the CubiCasa5K baseline model.

    Returns a mapping of semantic mask names to image paths. Implement this
    by loading a pretrained model and writing masks into the ml directory.
    """
    return {}


def postprocess_masks(masks: Dict[str, Path], scale: float) -> Plan:
    plan = empty_plan(scale=scale)
    return plan


def run_raster_track(page_images: List[Path], scale: float) -> Plan:
    merged_masks: Dict[str, Path] = {}
    for page in page_images:
        merged_masks.update(cubicasa_infer(page))
    return postprocess_masks(merged_masks, scale=scale)
