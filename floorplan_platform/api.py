from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from floorplan_platform.queue import enqueue
from floorplan_platform.storage import JobPaths, create_job, load_job, update_status

app = FastAPI(title="Floorplan Platform")


@app.post("/jobs")
async def create_job_endpoint(
    track: str = "raster",
    scale: float = 0.001,
    pdf: UploadFile = File(...),
) -> dict:
    if track not in {"vector", "raster"}:
        raise HTTPException(status_code=400, detail="track must be vector or raster")

    job = create_job()
    content = await pdf.read()
    job.input_pdf.write_bytes(content)
    update_status(job, "uploaded")
    return {"job_id": job.root.name, "status": "uploaded", "track": track, "scale": scale}


@app.post("/jobs/{job_id}/process")
def process_job_endpoint(job_id: str, track: str = "raster", scale: float = 0.001) -> dict:
    job = _get_job(job_id)
    update_status(job, "queued", {"track": track, "scale": str(scale)})
    mode = enqueue(job_id=job_id, track=track, scale=scale)
    return {"job_id": job_id, "status": "queued", "mode": mode}


@app.get("/jobs/{job_id}")
def job_status(job_id: str) -> dict:
    job = _get_job(job_id)
    return json.loads(job.metadata.read_text())


@app.get("/jobs/{job_id}/plan")
def get_plan(job_id: str) -> dict:
    job = _get_job(job_id)
    if not job.plan_json.exists():
        raise HTTPException(status_code=404, detail="plan.json not available")
    return json.loads(job.plan_json.read_text())


@app.get("/jobs/{job_id}/ifc")
def get_ifc(job_id: str) -> FileResponse:
    job = _get_job(job_id)
    if not job.ifc_path.exists():
        raise HTTPException(status_code=404, detail="IFC not available")
    return FileResponse(path=job.ifc_path, filename=job.ifc_path.name)


@app.get("/jobs/{job_id}/artifacts/{artifact_path:path}")
def get_artifact(job_id: str, artifact_path: str) -> FileResponse:
    job = _get_job(job_id)
    target = job.root / artifact_path
    if not target.exists():
        raise HTTPException(status_code=404, detail="artifact not found")
    return FileResponse(path=target, filename=target.name)


def _get_job(job_id: str) -> JobPaths:
    job = load_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job
