from pydantic import BaseModel, Field, model_validator


class Soil(BaseModel):
    soil_type: str | None = None

    sand_pct: float | None = Field(default=None, ge=0, le=100)
    silt_pct: float | None = Field(default=None, ge=0, le=100)
    clay_pct: float | None = Field(default=None, ge=0, le=100)

    field_capacity: float = Field(
        ...,
        gt=0,
        le=1,
        description="Contenido volumétrico de agua a capacidad de campo",
    )

    wilting_point: float = Field(
        ...,
        ge=0,
        lt=1,
        description="Contenido volumétrico de agua en punto de marchitez permanente",
    )

    saturation: float | None = Field(
        default=None,
        gt=0,
        le=1,
    )

    bulk_density_g_cm3: float | None = Field(
        default=None,
        gt=0,
    )

    root_zone_depth_m: float = Field(
        default=0.5,
        gt=0,
    )

    @model_validator(mode="after")
    def validate_hydraulic_properties(self):
        if self.wilting_point >= self.field_capacity:
            raise ValueError(
                "wilting_point debe ser menor que field_capacity."
            )

        if self.saturation is not None:
            if self.saturation <= self.field_capacity:
                raise ValueError(
                    "saturation debe ser mayor que field_capacity."
                )

        texture_values = [
            self.sand_pct,
            self.silt_pct,
            self.clay_pct,
        ]

        if all(value is not None for value in texture_values):
            total = sum(texture_values)

            if not 99 <= total <= 101:
                raise ValueError(
                    "sand_pct + silt_pct + clay_pct debe ser aproximadamente 100."
                )

        return self