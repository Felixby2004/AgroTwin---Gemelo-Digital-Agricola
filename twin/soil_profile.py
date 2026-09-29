from pydantic import BaseModel, Field

class SoilProfileSummary(BaseModel):
    depth_cm: int

    sand_pct: float | None = None
    silt_pct: float | None = None
    clay_pct: float | None = None

    bulk_density_g_cm3: float | None = None

    organic_carbon_g_kg: float | None = None

    ph_h2o: float | None = None

    water_content_33kpa_pct: float | None = None

    water_content_1500kpa_pct: float | None = None


class SoilLayer(BaseModel):
    depth_top_cm: int
    depth_bottom_cm: int

    sand_pct: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    silt_pct: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    clay_pct: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    bulk_density_g_cm3: float | None = Field(
        default=None,
        gt=0,
    )

    organic_carbon_g_kg: float | None = Field(
        default=None,
        ge=0,
    )

    ph_h2o: float | None = Field(
        default=None,
        ge=0,
        le=14,
    )

    water_content_33kpa_pct: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    water_content_1500kpa_pct: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )


class SoilProfile(BaseModel):
    latitude: float
    longitude: float

    source: str = "SOILGRIDS"

    layers: list[SoilLayer]

    @property
    def has_data(self) -> bool:
        return len(self.layers) > 0


    def summarize(
        self,
        max_depth_cm: int = 30,
    ) -> SoilProfileSummary:

        selected_layers = [
            layer
            for layer in self.layers
            if layer.depth_top_cm < max_depth_cm
        ]

        if not selected_layers:
            raise ValueError(
                "No existen capas dentro de la "
                "profundidad solicitada."
            )

        def weighted_average(
            attribute: str,
        ) -> float | None:

            numerator = 0.0
            denominator = 0.0

            for layer in selected_layers:

                value = getattr(
                    layer,
                    attribute,
                )

                if value is None:
                    continue

                bottom = min(
                    layer.depth_bottom_cm,
                    max_depth_cm,
                )

                thickness = (
                    bottom
                    -
                    layer.depth_top_cm
                )

                if thickness <= 0:
                    continue

                numerator += (
                    value
                    * thickness
                )

                denominator += thickness

            if denominator == 0:
                return None

            return (
                numerator
                /
                denominator
            )

        return SoilProfileSummary(
            depth_cm=max_depth_cm,

            sand_pct=weighted_average(
                "sand_pct"
            ),

            silt_pct=weighted_average(
                "silt_pct"
            ),

            clay_pct=weighted_average(
                "clay_pct"
            ),

            bulk_density_g_cm3=weighted_average(
                "bulk_density_g_cm3"
            ),

            organic_carbon_g_kg=weighted_average(
                "organic_carbon_g_kg"
            ),

            ph_h2o=weighted_average(
                "ph_h2o"
            ),

            water_content_33kpa_pct=weighted_average(
                "water_content_33kpa_pct"
            ),

            water_content_1500kpa_pct=weighted_average(
                "water_content_1500kpa_pct"
            ),
        )