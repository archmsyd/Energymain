# Floorplan Platform (Minimal)

This folder contains a minimal production-shaped scaffold for the floorplan-to-BIM platform.
It includes:

- FastAPI backend (`floorplan_platform/api.py`)
- Job storage and artifact layout (`floorplan_platform/storage.py`)
- Track A (vector) + Track B (raster) pipeline stubs (`floorplan_platform/pipeline`)
- IFC export stub (IfcOpenShell)
- Static frontend mockup (`floorplan_platform/frontend`)

## Running the API

```bash
pip install -r floorplan_platform/requirements.txt
uvicorn floorplan_platform.api:app --reload
```

## Running the frontend mockup

```bash
python -m http.server --directory floorplan_platform/frontend 5173
```
