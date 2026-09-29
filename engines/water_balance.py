from dataclasses import dataclass

from twin import TwinState


@dataclass
class WaterBalanceResult:
    initial_soil_moisture: float
    final_soil_moisture: float

    et0_mm: float
    etc_mm: float

    rainfall_mm: float
    effective_rainfall_mm: float

    irrigation_mm: float
    effective_irrigation_mm: float

    runoff_mm: float
    deep_percolation_mm: float

    root_zone_depletion_mm: float
    taw_mm: float
    raw_mm: float

    water_stress_index: float


class WaterBalanceEngine:
    """
    Motor simplificado de balance hídrico diario.

    Esta implementación inicial sirve como baseline
    antes de integrar AquaCrop.
    """

    def calculate_etc(self, state: TwinState) -> float:
        et0 = state.weather.et0_mm_day

        if et0 is None:
            raise ValueError(
                "ET0 es requerido para calcular ETc."
            )

        return et0 * state.crop.kc

    def calculate_taw(self, state: TwinState) -> float:
        """
        Total Available Water (TAW), en mm.

        TAW = 1000 * (FC - WP) * Zr
        """

        fc = state.soil.field_capacity
        wp = state.soil.wilting_point
        root_depth = state.crop.root_depth_m

        return 1000 * (fc - wp) * root_depth

    def calculate_raw(self, state: TwinState) -> float:
        """
        Readily Available Water (RAW), en mm.

        RAW = p * TAW
        """

        taw = self.calculate_taw(state)

        return state.crop.depletion_fraction_p * taw

    def calculate_root_zone_depletion(
        self,
        state: TwinState,
    ) -> float:
        """
        Déficit respecto a capacidad de campo.

        Dr = 1000 * (FC - theta) * Zr
        """

        fc = state.soil.field_capacity
        theta = state.soil_moisture
        root_depth = state.crop.root_depth_m

        depletion = 1000 * (fc - theta) * root_depth

        return max(0.0, depletion)

    def calculate_water_stress_index(
        self,
        depletion_mm: float,
        raw_mm: float,
        taw_mm: float,
    ) -> float:
        """
        Índice simplificado de estrés:

        0 = sin estrés
        1 = estrés máximo
        """

        if depletion_mm <= raw_mm:
            return 0.0

        denominator = taw_mm - raw_mm

        if denominator <= 0:
            return 1.0

        stress = (
            depletion_mm - raw_mm
        ) / denominator

        return max(0.0, min(1.0, stress))


    def calculate_effective_rainfall(
        self,
        rainfall_mm: float,
        efficiency: float = 0.90,
    ) -> float:
        """
        Aproximación inicial de precipitación efectiva.

        Más adelante podrá sustituirse por un modelo
        más agronómico o por AquaCrop.
        """

        if rainfall_mm < 0:
            raise ValueError(
                "La precipitación no puede ser negativa."
            )

        if not 0 <= efficiency <= 1:
            raise ValueError(
                "La eficiencia debe estar entre 0 y 1."
            )

        return rainfall_mm * efficiency


    def calculate_effective_irrigation(
        self,
        irrigation_mm: float,
        efficiency: float = 0.85,
    ) -> float:
        """
        Riego efectivo después de considerar pérdidas
        del sistema de aplicación.
        """

        if irrigation_mm < 0:
            raise ValueError(
                "El riego no puede ser negativo."
            )

        if not 0 < efficiency <= 1:
            raise ValueError(
                "La eficiencia debe estar entre 0 y 1."
            )

        return irrigation_mm * efficiency


    def mm_to_volumetric_fraction(
        self,
        water_mm: float,
        root_depth_m: float,
    ) -> float:
        """
        Convierte una lámina de agua en mm a
        fracción volumétrica para una profundidad radicular.
        """

        if root_depth_m <= 0:
            raise ValueError(
                "root_depth_m debe ser mayor que cero."
            )

        return water_mm / (1000 * root_depth_m)


    def step(
        self,
        state: TwinState,
        irrigation_mm: float = 0.0,
        irrigation_efficiency: float = 0.85,
        rainfall_efficiency: float = 0.90,
    ) -> WaterBalanceResult:

        etc_mm = self.calculate_etc(state)

        rainfall_mm = state.weather.rainfall_mm

        effective_rainfall_mm = (
            self.calculate_effective_rainfall(
                rainfall_mm,
                rainfall_efficiency,
            )
        )

        effective_irrigation_mm = (
            self.calculate_effective_irrigation(
                irrigation_mm,
                irrigation_efficiency,
            )
        )

        root_depth = state.crop.root_depth_m

        current_water_mm = (
            state.soil_moisture
            * 1000
            * root_depth
        )

        incoming_water_mm = (
            effective_rainfall_mm
            + effective_irrigation_mm
        )

        provisional_water_mm = (
            current_water_mm
            + incoming_water_mm
            - etc_mm
        )

        saturation = state.soil.saturation

        runoff_mm = 0.0
        deep_percolation_mm = 0.0

        if saturation is not None:
            saturation_water_mm = (
                saturation
                * 1000
                * root_depth
            )

            if provisional_water_mm > saturation_water_mm:
                excess = (
                    provisional_water_mm
                    - saturation_water_mm
                )

                deep_percolation_mm = excess
                provisional_water_mm = saturation_water_mm

        minimum_water_mm = (
            state.soil.wilting_point
            * 1000
            * root_depth
        )

        provisional_water_mm = max(
            minimum_water_mm,
            provisional_water_mm,
        )

        final_soil_moisture = (
            provisional_water_mm
            / (1000 * root_depth)
        )

        temp_state = state.model_copy(
            update={
                "soil_moisture": final_soil_moisture
            }
        )

        depletion_mm = (
            self.calculate_root_zone_depletion(
                temp_state
            )
        )

        taw_mm = self.calculate_taw(temp_state)
        raw_mm = self.calculate_raw(temp_state)

        stress = self.calculate_water_stress_index(
            depletion_mm,
            raw_mm,
            taw_mm,
        )

        return WaterBalanceResult(
            initial_soil_moisture=state.soil_moisture,
            final_soil_moisture=final_soil_moisture,

            et0_mm=state.weather.et0_mm_day,
            etc_mm=etc_mm,

            rainfall_mm=rainfall_mm,
            effective_rainfall_mm=effective_rainfall_mm,

            irrigation_mm=irrigation_mm,
            effective_irrigation_mm=effective_irrigation_mm,

            runoff_mm=runoff_mm,
            deep_percolation_mm=deep_percolation_mm,

            root_zone_depletion_mm=depletion_mm,
            taw_mm=taw_mm,
            raw_mm=raw_mm,

            water_stress_index=stress,
        )


    def update_state(
        self,
        state: TwinState,
        result: WaterBalanceResult,
    ) -> TwinState:

        return state.model_copy(
            update={
                "previous_soil_moisture": state.soil_moisture,
                "soil_moisture": result.final_soil_moisture,
                "etc_mm_day": result.etc_mm,
                "root_zone_depletion_mm": (
                    result.root_zone_depletion_mm
                ),
                "water_stress_index": (
                    result.water_stress_index
                ),
                "last_irrigation_mm": result.irrigation_mm,
            }
        )