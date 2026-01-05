from __future__ import annotations

from pathlib import Path

from floorplan_platform.models import Plan


def write_ifc(plan: Plan, output_path: Path) -> None:
    try:
        import ifcopenshell
        import ifcopenshell.api
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ImportError("IfcOpenShell is required for IFC export.") from exc

    model = ifcopenshell.file()
    project = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject", name="Floorplan Project")
    site = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSite", name="Site")
    building = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuilding", name="Building")

    ifcopenshell.api.run("aggregate.assign_object", model, relating_object=project, product=site)
    ifcopenshell.api.run("aggregate.assign_object", model, relating_object=site, product=building)

    for floor in plan.floors:
        storey = ifcopenshell.api.run(
            "root.create_entity",
            model,
            ifc_class="IfcBuildingStorey",
            name=floor.name,
        )
        ifcopenshell.api.run("aggregate.assign_object", model, relating_object=building, product=storey)

    model.write(str(output_path))
