from dataclasses import dataclass

from twin import (
    Soil,
    SoilProfile,
)


class SoilHydraulicError(Exception):
    """Error al derivar propiedades hidráulicas."""


@dataclass
class SoilHydraulicResult:

    field_capacity: float
    wilting_point: float

    available_water_capacity: float

    source: str

    depth_cm: int


class SoilHydraulicEstimator:

    def from_soilgrids(
        self,
        profile: SoilProfile,
        max_depth_cm: int = 30,
    ) -> SoilHydraulicResult:

        summary = profile.summarize(
            max_depth_cm=max_depth_cm
        )

        fc_pct = (
            summary.water_content_33kpa_pct
        )

        wp_pct = (
            summary.water_content_1500kpa_pct
        )

        if fc_pct is None:
            raise SoilHydraulicError(
                "SoilGrids no devolvió wv003."
            )

        if wp_pct is None:
            raise SoilHydraulicError(
                "SoilGrids no devolvió wv1500."
            )

        field_capacity = (
            fc_pct / 100.0
        )

        wilting_point = (
            wp_pct / 100.0
        )

        if wilting_point >= field_capacity:
            raise SoilHydraulicError(
                "El punto de marchitez debe ser "
                "menor que la capacidad de campo."
            )

        available_water_capacity = (
            field_capacity
            -
            wilting_point
        )

        return SoilHydraulicResult(
            field_capacity=field_capacity,
            wilting_point=wilting_point,
            available_water_capacity=(
                available_water_capacity
            ),
            source=(
                "SOILGRIDS_WV003_WV1500"
            ),
            depth_cm=max_depth_cm,
        )


    def build_soil(
        self,
        profile: SoilProfile,
        root_zone_depth_m: float = 0.30,
    ) -> Soil:

        max_depth_cm = int(
            root_zone_depth_m
            * 100
        )

        summary = profile.summarize(
            max_depth_cm=max_depth_cm
        )

        hydraulic = self.from_soilgrids(
            profile=profile,
            max_depth_cm=max_depth_cm,
        )

        if (
            summary.sand_pct is None
            or summary.silt_pct is None
            or summary.clay_pct is None
        ):
            raise SoilHydraulicError(
                "No existe información suficiente "
                "de textura para construir Soil."
            )

        return Soil(
            soil_type=None,

            sand_pct=summary.sand_pct,
            silt_pct=summary.silt_pct,
            clay_pct=summary.clay_pct,

            field_capacity=(
                hydraulic.field_capacity
            ),

            wilting_point=(
                hydraulic.wilting_point
            ),

            saturation=None,

            bulk_density_g_cm3=(
                summary.bulk_density_g_cm3
            ),

            root_zone_depth_m=(
                root_zone_depth_m
            ),
        )