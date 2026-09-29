from pydantic import BaseModel, Field


class Parcel(BaseModel):
    parcel_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

    area_ha: float = Field(..., gt=0)

    elevation_m: float | None = None
    slope_pct: float | None = Field(default=None, ge=0)

    irrigation_system: str | None = None

    def __str__(self) -> str:
        return f"{self.name} ({self.area_ha} ha)"