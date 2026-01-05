from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from floorplan_platform.models import Plan, empty_plan


def extract_vector_primitives(pdf_path: Path) -> Dict[str, List[dict]]:
    """Extract vector primitives from a CAD-exported PDF.

    This is a placeholder that should be replaced with a PDF vector parser
    (for example, pdfminer.six or custom PDF parsing) to extract lines, arcs,
    and text. The output structure is intentionally generic.
    """
    return {"lines": [], "arcs": [], "text": []}


def reconstruct_plan_from_vectors(primitives: Dict[str, List[dict]], scale: float) -> Plan:
    plan = empty_plan(scale=scale)
    return plan


def run_vector_track(pdf_path: Path, scale: float) -> Plan:
    primitives = extract_vector_primitives(pdf_path)
    return reconstruct_plan_from_vectors(primitives, scale=scale)
