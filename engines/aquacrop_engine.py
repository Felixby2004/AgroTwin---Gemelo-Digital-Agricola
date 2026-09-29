from dataclasses import dataclass

import pandas as pd

from aquacrop import (
    AquaCropModel,
    Soil as AquaCropSoil,
    Crop as AquaCropCrop,
    InitialWaterContent,
    IrrigationManagement,
)

from twin import (
    Soil as TwinSoil,
    SoilProfile,
    WeatherState,
)

class AquaCropEngineError(Exception):
    """Error específico del motor AquaCrop."""


@dataclass
class AquaCropSoilParameters:
    sand_pct: float
    silt_pct: float | None
    clay_pct: float

    field_capacity: float
    wilting_point: float

    saturation: float | None
    ksat_mm_day: float | None

    bulk_density_g_cm3: float | None

    root_zone_depth_m: float


@dataclass
class AquaCropSimulationResult:
    model: object

    final_stats: pd.DataFrame
    water_flux: pd.DataFrame
    water_storage: pd.DataFrame
    crop_growth: pd.DataFrame

class AquaCropEngine:

    def map_soil(
        self,
        soil: TwinSoil,
    ) -> AquaCropSoilParameters:

        if soil.sand_pct is None:
            raise AquaCropEngineError(
                "Se requiere sand_pct para AquaCrop."
            )

        if soil.clay_pct is None:
            raise AquaCropEngineError(
                "Se requiere clay_pct para AquaCrop."
            )

        if (
            soil.wilting_point
            >= soil.field_capacity
        ):
            raise AquaCropEngineError(
                "wilting_point debe ser menor que field_capacity."
            )

        return AquaCropSoilParameters(
            sand_pct=soil.sand_pct,
            silt_pct=soil.silt_pct,
            clay_pct=soil.clay_pct,

            field_capacity=soil.field_capacity,
            wilting_point=soil.wilting_point,

            saturation=soil.saturation,

            ksat_mm_day=None,

            bulk_density_g_cm3=(
                soil.bulk_density_g_cm3
            ),

            root_zone_depth_m=(
                soil.root_zone_depth_m
            ),
    )


    def map_weather(
        self,
        weather_series: list[WeatherState],
    ) -> pd.DataFrame:

        if not weather_series:
            raise AquaCropEngineError(
                "weather_series no puede estar vacío."
            )

        rows = []

        for weather in sorted(
            weather_series,
            key=lambda w: w.timestamp,
        ):

            if weather.temperature_min_c is None:
                raise AquaCropEngineError(
                    "AquaCrop requiere temperature_min_c."
                )

            if weather.temperature_max_c is None:
                raise AquaCropEngineError(
                    "AquaCrop requiere temperature_max_c."
                )

            if weather.et0_mm_day is None:
                raise AquaCropEngineError(
                    "AquaCrop requiere ET0."
                )

            rows.append(
                {
                    "MinTemp": float(
                        weather.temperature_min_c
                    ),

                    "MaxTemp": float(
                        weather.temperature_max_c
                    ),

                    "Precipitation": float(
                        weather.rainfall_mm
                    ),

                    "ReferenceET": max(
                        0.1,
                        float(
                            weather.et0_mm_day
                        ),
                    ),

                    "Date": pd.Timestamp(
                        weather.timestamp.date()
                    ),
                }
            )

        # -------------------------------------------------
        # IMPORTANTE:
        # AquaCrop 3.1.0 internamente depende del orden
        # producido por prepare_weather().
        # -------------------------------------------------

        df = pd.DataFrame(
            rows,
            columns=[
                "MinTemp",
                "MaxTemp",
                "Precipitation",
                "ReferenceET",
                "Date",
            ],
        )

        # Garantizar tipos explícitos
        numeric_columns = [
            "MinTemp",
            "MaxTemp",
            "Precipitation",
            "ReferenceET",
        ]

        for column in numeric_columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="raise",
            ).astype(float)

        df["Date"] = pd.to_datetime(
            df["Date"]
        )

        return df


    CROP_NAME_MAP = {
        "Maíz": "Maize",
        "Tomate": "Tomato",
        "Papa": "Potato",
        "Arroz": "PaddyRice",
    }


    def map_crop_name(
        self,
        crop_name: str,
    ) -> str:

        if crop_name not in self.CROP_NAME_MAP:
            raise AquaCropEngineError(
                f"El cultivo '{crop_name}' todavía "
                "no está mapeado a AquaCrop."
            )

        return self.CROP_NAME_MAP[
            crop_name
        ]


    def build_aquacrop_soil(
        self,
        soil: TwinSoil,
        organic_carbon_g_kg: float | None = None,
    ) -> AquaCropSoil:

        params = self.map_soil(
            soil
        )

        # Perfil AquaCrop.
        # Usamos compartimentos de 0.1 m.
        profile_depth = max(
            1.0,
            params.root_zone_depth_m,
        )

        n_compartments = int(
            round(
                profile_depth / 0.1
            )
        )

        dz = [
            0.1
            for _ in range(
                n_compartments
            )
        ]

        aqua_soil = AquaCropSoil(
            soil_type="custom",
            dz=dz,
        )

        # ---------------------------------------------
        # Convertir SOC a materia orgánica
        # ---------------------------------------------

        if organic_carbon_g_kg is None:
            organic_matter_pct = 2.0

        else:

            soc_pct = (
                organic_carbon_g_kg
                / 10.0
            )

            organic_matter_pct = (
                soc_pct
                * 1.724
            )

        # ---------------------------------------------
        # Crear suelo temporal con pedotransferencia
        # AquaCrop para obtener thS y Ksat
        # ---------------------------------------------

        temporary_soil = AquaCropSoil(
            soil_type="custom",
            dz=dz,
        )

        temporary_soil.add_layer_from_texture(
            thickness=profile_depth,
            Sand=params.sand_pct,
            Clay=params.clay_pct,
            OrgMat=organic_matter_pct,
            penetrability=100,
        )

        temp_profile = (
            temporary_soil.profile
            .dropna(
                subset=[
                    "th_s",
                    "Ksat",
                ]
            )
        )

        if temp_profile.empty:
            raise AquaCropEngineError(
                "AquaCrop no pudo estimar "
                "thS y Ksat a partir de la textura."
            )

        estimated_th_s = float(
            temp_profile.iloc[0][
                "th_s"
            ]
        )

        estimated_ksat = float(
            temp_profile.iloc[0][
                "Ksat"
            ]
        )

        # ---------------------------------------------
        # Validar relación hidráulica
        # ---------------------------------------------

        if (
            params.field_capacity
            >= estimated_th_s
        ):
            raise AquaCropEngineError(
                "La capacidad de campo derivada "
                "es mayor o igual que la saturación "
                "estimada por AquaCrop."
            )

        # ---------------------------------------------
        # Capa definitiva
        # ---------------------------------------------

        aqua_soil.add_layer(
            thickness=profile_depth,

            thWP=params.wilting_point,

            thFC=params.field_capacity,

            thS=estimated_th_s,

            Ksat=estimated_ksat,

            penetrability=100,
        )

        return aqua_soil


    def build_aquacrop_crop(
        self,
        crop_name: str,
        planting_date,
        harvest_date=None,
    ):

        aqua_name = self.map_crop_name(
            crop_name
        )

        planting_str = (
            planting_date.strftime(
                "%m/%d"
            )
        )

        harvest_str = None

        if harvest_date is not None:
            harvest_str = (
                harvest_date.strftime(
                    "%m/%d"
                )
            )

        return AquaCropCrop(
            aqua_name,
            planting_date=planting_str,
            harvest_date=harvest_str,
        )
    

    def build_initial_water_content(
        self,
        soil_moisture: float,
        profile_depth_m: float,
    ) -> InitialWaterContent:

        if not 0 <= soil_moisture <= 1:
            raise AquaCropEngineError(
                "soil_moisture debe estar entre 0 y 1."
            )

        if profile_depth_m <= 0:
            raise AquaCropEngineError(
                "profile_depth_m debe ser mayor que 0."
            )

        return InitialWaterContent(
            wc_type="Num",
            method="Depth",
            depth_layer=[
                float(profile_depth_m),
            ],
            value=[
                float(soil_moisture),
            ],
        )


    def build_irrigation_management(
        self,
        irrigation_schedule: dict,
    ) -> IrrigationManagement:

        if not irrigation_schedule:

            return IrrigationManagement(
                irrigation_method=0
            )

        rows = []

        for irrigation_date, depth_mm in sorted(
            irrigation_schedule.items()
        ):

            if depth_mm < 0:
                raise AquaCropEngineError(
                    "El riego no puede ser negativo."
                )

            if depth_mm == 0:
                continue

            rows.append(
                {
                    "Date": pd.Timestamp(
                        irrigation_date
                    ),
                    "Depth": float(
                        depth_mm
                    ),
                }
            )

        if not rows:

            return IrrigationManagement(
                irrigation_method=0
            )

        schedule_df = pd.DataFrame(
            rows,
            columns=[
                "Date",
                "Depth",
            ],
        )

        return IrrigationManagement(
            irrigation_method=3,
            Schedule=schedule_df,
            MaxIrr=1000.0,
        )


    def simulate(
        self,
        weather_series,
        soil,
        crop_name,
        planting_date,
        simulation_start_date,
        simulation_end_date,
        initial_soil_moisture,
        irrigation_schedule=None,
        organic_carbon_g_kg=None,
        soil_profile: SoilProfile | None = None,

    ) -> AquaCropSimulationResult:

        if simulation_end_date < simulation_start_date:
            raise AquaCropEngineError(
                "simulation_end_date debe ser posterior "
                "a simulation_start_date."
            )

        weather_df = self.map_weather(
            weather_series
        )

        expected_columns = [
            "MinTemp",
            "MaxTemp",
            "Precipitation",
            "ReferenceET",
            "Date",
        ]

        if list(weather_df.columns) != expected_columns:
            raise AquaCropEngineError(
                "Orden inválido de columnas meteorológicas "
                "para AquaCrop. "
                f"Recibido: {list(weather_df.columns)}"
            )


        for column in [
            "MinTemp",
            "MaxTemp",
            "Precipitation",
            "ReferenceET",
        ]:
            if not pd.api.types.is_numeric_dtype(
                weather_df[column]
            ):
                raise AquaCropEngineError(
                    f"La columna {column} debe ser numérica."
                )

        if not pd.api.types.is_datetime64_any_dtype(
            weather_df["Date"]
        ):
            raise AquaCropEngineError(
                "La columna Date debe ser datetime."
            )


        if soil_profile is not None:
            aqua_soil = self.build_aquacrop_soil_from_profile(
                soil_profile
            )
        else:
            aqua_soil = self.build_aquacrop_soil(
                soil=soil,
                organic_carbon_g_kg=organic_carbon_g_kg,
            )

        aqua_crop = self.build_aquacrop_crop(
            crop_name=crop_name,
            planting_date=planting_date,
        )

        profile_depth_m = float(aqua_soil.zSoil)
        original_zmax = float(aqua_crop.Zmax)

        root_depth_constrained = False

        if original_zmax > profile_depth_m:
            aqua_crop.Zmax = profile_depth_m
            root_depth_constrained = True


        initial_water = (
            self.build_initial_water_content(
                soil_moisture=initial_soil_moisture,
                profile_depth_m=profile_depth_m,
            )
        )

        irrigation_management = (
            self.build_irrigation_management(
                irrigation_schedule
                or {}
            )
        )

        try:

            model = AquaCropModel(
                sim_start_time=(
                    simulation_start_date.strftime(
                        "%Y/%m/%d"
                    )
                ),
                sim_end_time=(
                    simulation_end_date.strftime(
                        "%Y/%m/%d"
                    )
                ),
                weather_df=weather_df,
                soil=aqua_soil,
                crop=aqua_crop,
                initial_water_content=(
                    initial_water
                ),
                irrigation_management=(
                    irrigation_management
                ),
            )

            model.run_model(
                till_termination=True
            )

        except Exception as exc:

            raise AquaCropEngineError(
                "AquaCrop no pudo ejecutar "
                f"la simulación: {exc}"
            ) from exc

        outputs = model._outputs

        return AquaCropSimulationResult(
            model=model,

            final_stats=(
                outputs.final_stats.copy()
            ),

            water_flux=(
                outputs.water_flux.copy()
            ),

            water_storage=(
                outputs.water_storage.copy()
            ),

            crop_growth=(
                outputs.crop_growth.copy()
            ),
        )


    @staticmethod
    def organic_carbon_to_organic_matter_pct(
        organic_carbon_g_kg: float | None,
    ) -> float:

        if organic_carbon_g_kg is None:
            return 2.0

        soc_pct = (
            organic_carbon_g_kg
            / 10.0
        )

        organic_matter_pct = (
            soc_pct
            * 1.724
        )

        return organic_matter_pct


    def build_aquacrop_soil_from_profile(
        self,
        profile: SoilProfile,
    ) -> AquaCropSoil:

        if not profile.layers:
            raise AquaCropEngineError(
                "El perfil SoilGrids no contiene capas."
            )

        layers = sorted(
            profile.layers,
            key=lambda layer: layer.depth_top_cm,
        )

        # -------------------------------------------------
        # Validar continuidad y encontrar profundidad total
        # -------------------------------------------------

        expected_top = 0

        for layer in layers:

            if layer.depth_top_cm != expected_top:
                raise AquaCropEngineError(
                    "El perfil de suelo no es continuo. "
                    f"Se esperaba una capa desde {expected_top} cm "
                    f"pero se encontró {layer.depth_top_cm} cm."
                )

            if (
                layer.depth_bottom_cm
                <=
                layer.depth_top_cm
            ):
                raise AquaCropEngineError(
                    "Profundidad inválida en una capa SoilGrids."
                )

            expected_top = (
                layer.depth_bottom_cm
            )

        profile_depth_m = (
            layers[-1].depth_bottom_cm
            / 100.0
        )

        # -------------------------------------------------
        # Compartimentos AquaCrop
        #
        # Mantendremos límites exactos en:
        # 5, 15 y 30 cm.
        # Desde 30 cm usamos compartimentos de 10 cm.
        # -------------------------------------------------

        dz = [
            0.05,
            0.10,
            0.15,
        ]

        remaining_depth = (
            profile_depth_m
            - 0.30
        )

        while remaining_depth > 1e-9:

            compartment = min(
                0.10,
                remaining_depth,
            )

            dz.append(
                round(
                    compartment,
                    6,
                )
            )

            remaining_depth -= compartment

        aqua_soil = AquaCropSoil(
            soil_type="custom",
            dz=dz,
        )

        # -------------------------------------------------
        # Crear las capas hidráulicas
        # -------------------------------------------------

        for layer in layers:

            required_values = {
                "sand_pct":
                    layer.sand_pct,

                "clay_pct":
                    layer.clay_pct,

                "water_content_33kpa_pct":
                    layer.water_content_33kpa_pct,

                "water_content_1500kpa_pct":
                    layer.water_content_1500kpa_pct,
            }

            missing = [
                name
                for name, value
                in required_values.items()
                if value is None
            ]

            if missing:

                raise AquaCropEngineError(
                    "Faltan datos para construir "
                    f"la capa {layer.depth_top_cm}-"
                    f"{layer.depth_bottom_cm} cm: "
                    f"{missing}"
                )

            thickness_m = (
                layer.depth_bottom_cm
                -
                layer.depth_top_cm
            ) / 100.0

            th_fc = (
                layer.water_content_33kpa_pct
                / 100.0
            )

            th_wp = (
                layer.water_content_1500kpa_pct
                / 100.0
            )

            organic_matter_pct = (
                self
                .organic_carbon_to_organic_matter_pct(
                    layer.organic_carbon_g_kg
                )
            )

            # ---------------------------------------------
            # Pedotransferencia AquaCrop
            #
            # Nos interesan principalmente thS y Ksat.
            # FC y WP serán los observados por SoilGrids.
            # ---------------------------------------------

            (
                _estimated_wp,
                _estimated_fc,
                estimated_saturation,
                estimated_ksat,
            ) = (
                aqua_soil
                .calculate_soil_hydraulic_properties(
                    layer.sand_pct / 100.0,
                    layer.clay_pct / 100.0,
                    organic_matter_pct,
                )
            )

            if th_wp >= th_fc:
                raise AquaCropEngineError(
                    f"WP >= FC en capa "
                    f"{layer.depth_top_cm}-"
                    f"{layer.depth_bottom_cm} cm."
                )

            if th_fc >= estimated_saturation:
                raise AquaCropEngineError(
                    f"FC >= saturación estimada "
                    f"en capa "
                    f"{layer.depth_top_cm}-"
                    f"{layer.depth_bottom_cm} cm."
                )

            if estimated_ksat <= 0:
                raise AquaCropEngineError(
                    f"Ksat inválido en capa "
                    f"{layer.depth_top_cm}-"
                    f"{layer.depth_bottom_cm} cm."
                )

            aqua_soil.add_layer(
                thickness=thickness_m,

                thWP=th_wp,
                thFC=th_fc,

                thS=float(
                    estimated_saturation
                ),

                Ksat=float(
                    estimated_ksat
                ),

                penetrability=100,
            )

        expected_depth_m = (
            layers[-1].depth_bottom_cm
            / 100.0
        )

        actual_depth_m = float(
            aqua_soil.zSoil
        )

        if abs(
            actual_depth_m
            - expected_depth_m
        ) > 1e-6:

            raise AquaCropEngineError(
                "La profundidad del perfil AquaCrop "
                "no coincide con el perfil SoilGrids. "
                f"Esperado={expected_depth_m:.2f} m, "
                f"obtenido={actual_depth_m:.2f} m."
            )

        return aqua_soil