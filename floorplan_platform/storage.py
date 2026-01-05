from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


DEFAULT_JOBS_DIR = Path(os.environ.get("FLOORPLAN_JOBS_DIR", "var/jobs"))


@dataclass(frozen=True)
class JobPaths:
    root: Path

    @property
    def input_pdf(self) -> Path:
        return self.root / "input.pdf"

    @property
    def pages_dir(self) -> Path:
        return self.root / "pages"

    @property
    def ml_dir(self) -> Path:
        return self.root / "ml"

    @property
    def vectors_dir(self) -> Path:
        return self.root / "vectors"

    @property
    def bim_dir(self) -> Path:
        return self.root / "bim"

    @property
    def metadata(self) -> Path:
        return self.root / "job.json"

    @property
    def plan_json(self) -> Path:
        return self.vectors_dir / "plan.json"

    @property
    def ifc_path(self) -> Path:
        return self.bim_dir / "model.ifc"


def create_job() -> JobPaths:
    job_id = uuid.uuid4().hex
    root = DEFAULT_JOBS_DIR / job_id
    root.mkdir(parents=True, exist_ok=False)
    (root / "pages").mkdir()
    (root / "ml").mkdir()
    (root / "vectors").mkdir()
    (root / "bim").mkdir()
    metadata = {"job_id": job_id, "status": "created"}
    (root / "job.json").write_text(json.dumps(metadata, indent=2))
    return JobPaths(root=root)


def load_job(job_id: str) -> Optional[JobPaths]:
    root = DEFAULT_JOBS_DIR / job_id
    if not root.exists():
        return None
    return JobPaths(root=root)


def update_status(job: JobPaths, status: str, extra: Optional[Dict[str, str]] = None) -> None:
    payload = {"job_id": job.root.name, "status": status}
    if extra:
        payload.update(extra)
    job.metadata.write_text(json.dumps(payload, indent=2))
