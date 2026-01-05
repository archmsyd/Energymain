from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Wall(BaseModel):
    id: str
    polyline: List[List[float]]
    thickness: float = Field(..., gt=0)
    height: float = Field(..., gt=0)


class Opening(BaseModel):
    id: str
    type: Literal["door", "window"]
    center: List[float]
    width: float = Field(..., gt=0)
    height: float = Field(..., gt=0)
    host_wall: Optional[str] = None
    sill: Optional[float] = None


class Space(BaseModel):
    id: str
    name: str
    polygon: List[List[float]]


class FloorPlan(BaseModel):
    name: str
    elevation: float
    walls: List[Wall] = Field(default_factory=list)
    openings: List[Opening] = Field(default_factory=list)
    spaces: List[Space] = Field(default_factory=list)


class Plan(BaseModel):
    units: Literal["m", "cm", "mm"] = "m"
    scale: float = Field(1.0, gt=0)
    floors: List[FloorPlan] = Field(default_factory=list)


def empty_plan(scale: float, floor_name: str = "Level 01") -> Plan:
    return Plan(
        units="m",
        scale=scale,
        floors=[FloorPlan(name=floor_name, elevation=0.0)],
    )
