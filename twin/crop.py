from datetime import date

from pydantic import BaseModel, Field


class Crop(BaseModel):
    crop_name: str = Field(..., min_length=1)

    variety: str | None = None

    planting_date: date

    growth_stage: str | None = None

    kc: float = Field(
        default=1.0,
        gt=0,
        le=2,
        description="Coeficiente de cultivo actual",
    )

    root_depth_m: float = Field(
        default=0.5,
        gt=0,
    )

    depletion_fraction_p: float = Field(
        default=0.5,
        gt=0,
        lt=1,
        description="Fracción de agotamiento tolerable",
    )