from __future__ import annotations

import json
from pathlib import Path

from floorplan_platform.models import Plan
from floorplan_platform.pipeline.ifc_writer import write_ifc
from floorplan_platform.pipeline.pdf_render import render_pdf_to_images
from floorplan_platform.pipeline.raster_track import run_raster_track
from floorplan_platform.pipeline.vector_track import run_vector_track
from floorplan_platform.storage import JobPaths, load_job, update_status


class JobNotFoundError(RuntimeError):
    pass


def _write_plan(plan: Plan, path: Path) -> None:
    path.write_text(plan.model_dump_json(indent=2))


def process_job(job_id: str, track: str, scale: float) -> None:
    job = load_job(job_id)
    if job is None:
        raise JobNotFoundError(job_id)

    update_status(job, "processing", {"track": track})
    if track == "vector":
        plan = run_vector_track(job.input_pdf, scale=scale)
    elif track == "raster":
        page_images = render_pdf_to_images(job.input_pdf, job.pages_dir, dpi=450)
        plan = run_raster_track(page_images, scale=scale)
    else:
        raise ValueError(f"Unknown track: {track}")

    _write_plan(plan, job.plan_json)
    _write_ifc(plan, job)
    update_status(job, "completed")


def _write_ifc(plan: Plan, job: JobPaths) -> None:
    try:
        write_ifc(plan, job.ifc_path)
    except ImportError:
        update_status(job, "completed", {"warning": "IfcOpenShell not installed"})
