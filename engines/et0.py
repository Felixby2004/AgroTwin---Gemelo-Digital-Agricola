import math
from dataclasses import dataclass
from datetime import date


@dataclass
class ET0Input:
    calculation_date: date

    latitude_deg: float
    elevation_m: float

    temperature_mean_c: float
    temperature_min_c: float
    temperature_max_c: float

    relative_humidity_pct: float

    solar_radiation_mj_m2_day: float

    wind_speed_m_s: float


@dataclass
class ET0Result:
    et0_mm_day: float

    net_radiation_mj_m2_day: float

    saturation_vapor_pressure_kpa: float
    actual_vapor_pressure_kpa: float

    vapor_pressure_deficit_kpa: float

    slope_vapor_pressure_curve_kpa_c: float

    psychrometric_constant_kpa_c: float

    extraterrestrial_radiation_mj_m2_day: float

    clear_sky_radiation_mj_m2_day: float


class ET0Calculator:
    """
    Evapotranspiración de referencia mediante
    FAO-56 Penman-Monteith.

    Esta implementación trabaja con datos diarios.
    """

    STEFAN_BOLTZMANN = 4.903e-9

    ALBEDO = 0.23

    def calculate(
        self,
        data: ET0Input,
    ) -> ET0Result:

        self._validate_input(data)

        es_tmin = self.saturation_vapor_pressure(
            data.temperature_min_c
        )

        es_tmax = self.saturation_vapor_pressure(
            data.temperature_max_c
        )

        es = (
            es_tmin + es_tmax
        ) / 2

        # Aproximación usando humedad relativa media.
        ea = (
            data.relative_humidity_pct
            / 100
        ) * es

        vapor_pressure_deficit = max(
            0.0,
            es - ea,
        )

        delta = self.slope_vapor_pressure_curve(
            data.temperature_mean_c
        )

        pressure = self.atmospheric_pressure(
            data.elevation_m
        )

        gamma = (
            0.000665
            * pressure
        )

        day_of_year = (
            data.calculation_date.timetuple().tm_yday
        )

        ra = self.extraterrestrial_radiation(
            latitude_deg=data.latitude_deg,
            day_of_year=day_of_year,
        )

        rso = self.clear_sky_radiation(
            extraterrestrial_radiation=ra,
            elevation_m=data.elevation_m,
        )

        rns = self.net_shortwave_radiation(
            data.solar_radiation_mj_m2_day
        )

        rnl = self.net_longwave_radiation(
            temperature_min_c=(
                data.temperature_min_c
            ),
            temperature_max_c=(
                data.temperature_max_c
            ),
            actual_vapor_pressure_kpa=ea,
            solar_radiation_mj_m2_day=(
                data.solar_radiation_mj_m2_day
            ),
            clear_sky_radiation_mj_m2_day=rso,
        )

        rn = rns - rnl

        # Para periodo diario:
        g = 0.0

        numerator = (
            0.408
            * delta
            * (rn - g)
            +
            gamma
            * (
                900
                /
                (
                    data.temperature_mean_c
                    + 273
                )
            )
            * data.wind_speed_m_s
            * vapor_pressure_deficit
        )

        denominator = (
            delta
            +
            gamma
            * (
                1
                +
                0.34
                * data.wind_speed_m_s
            )
        )

        if denominator <= 0:
            raise ValueError(
                "El denominador de Penman-Monteith "
                "no puede ser cero o negativo."
            )

        et0 = numerator / denominator

        et0 = max(
            0.0,
            et0,
        )

        return ET0Result(
            et0_mm_day=et0,

            net_radiation_mj_m2_day=rn,

            saturation_vapor_pressure_kpa=es,

            actual_vapor_pressure_kpa=ea,

            vapor_pressure_deficit_kpa=(
                vapor_pressure_deficit
            ),

            slope_vapor_pressure_curve_kpa_c=(
                delta
            ),

            psychrometric_constant_kpa_c=(
                gamma
            ),

            extraterrestrial_radiation_mj_m2_day=ra,

            clear_sky_radiation_mj_m2_day=rso,
        )

    @staticmethod
    def saturation_vapor_pressure(
        temperature_c: float,
    ) -> float:

        return (
            0.6108
            *
            math.exp(
                (
                    17.27
                    * temperature_c
                )
                /
                (
                    temperature_c
                    + 237.3
                )
            )
        )

    def slope_vapor_pressure_curve(
        self,
        temperature_c: float,
    ) -> float:

        es = self.saturation_vapor_pressure(
            temperature_c
        )

        return (
            4098
            * es
            /
            (
                temperature_c
                + 237.3
            ) ** 2
        )

    @staticmethod
    def atmospheric_pressure(
        elevation_m: float,
    ) -> float:

        return (
            101.3
            *
            (
                (
                    293
                    -
                    0.0065
                    * elevation_m
                )
                /
                293
            )
            ** 5.26
        )

    @staticmethod
    def inverse_relative_distance_earth_sun(
        day_of_year: int,
    ) -> float:

        return (
            1
            +
            0.033
            *
            math.cos(
                (
                    2
                    * math.pi
                    / 365
                )
                * day_of_year
            )
        )

    @staticmethod
    def solar_declination(
        day_of_year: int,
    ) -> float:

        return (
            0.409
            *
            math.sin(
                (
                    2
                    * math.pi
                    / 365
                )
                * day_of_year
                -
                1.39
            )
        )

    @staticmethod
    def sunset_hour_angle(
        latitude_rad: float,
        solar_declination_rad: float,
    ) -> float:

        value = (
            -math.tan(latitude_rad)
            * math.tan(
                solar_declination_rad
            )
        )

        # Protección por errores numéricos.
        value = max(
            -1.0,
            min(1.0, value),
        )

        return math.acos(value)

    def extraterrestrial_radiation(
        self,
        latitude_deg: float,
        day_of_year: int,
    ) -> float:

        latitude_rad = math.radians(
            latitude_deg
        )

        dr = (
            self.inverse_relative_distance_earth_sun(
                day_of_year
            )
        )

        solar_declination = (
            self.solar_declination(
                day_of_year
            )
        )

        sunset_angle = (
            self.sunset_hour_angle(
                latitude_rad,
                solar_declination,
            )
        )

        solar_constant = 0.0820

        ra = (
            (
                24
                * 60
                / math.pi
            )
            *
            solar_constant
            *
            dr
            *
            (
                sunset_angle
                * math.sin(latitude_rad)
                * math.sin(
                    solar_declination
                )
                +
                math.cos(latitude_rad)
                * math.cos(
                    solar_declination
                )
                * math.sin(
                    sunset_angle
                )
            )
        )

        return max(
            0.0,
            ra,
        )

    @staticmethod
    def clear_sky_radiation(
        extraterrestrial_radiation: float,
        elevation_m: float,
    ) -> float:

        return (
            0.75
            +
            2e-5
            * elevation_m
        ) * extraterrestrial_radiation

    def net_shortwave_radiation(
        self,
        solar_radiation_mj_m2_day: float,
    ) -> float:

        return (
            1
            -
            self.ALBEDO
        ) * solar_radiation_mj_m2_day

    def net_longwave_radiation(
        self,
        temperature_min_c: float,
        temperature_max_c: float,
        actual_vapor_pressure_kpa: float,
        solar_radiation_mj_m2_day: float,
        clear_sky_radiation_mj_m2_day: float,
    ) -> float:

        tmin_k = (
            temperature_min_c
            + 273.16
        )

        tmax_k = (
            temperature_max_c
            + 273.16
        )

        if clear_sky_radiation_mj_m2_day <= 0:
            radiation_ratio = 0.0
        else:
            radiation_ratio = (
                solar_radiation_mj_m2_day
                /
                clear_sky_radiation_mj_m2_day
            )

        # FAO recomienda limitar Rs/Rso.
        radiation_ratio = max(
            0.0,
            min(
                1.0,
                radiation_ratio,
            ),
        )

        rnl = (
            self.STEFAN_BOLTZMANN
            *
            (
                (
                    tmax_k ** 4
                    +
                    tmin_k ** 4
                )
                /
                2
            )
            *
            (
                0.34
                -
                0.14
                *
                math.sqrt(
                    max(
                        0.0,
                        actual_vapor_pressure_kpa,
                    )
                )
            )
            *
            (
                1.35
                * radiation_ratio
                -
                0.35
            )
        )

        return max(
            0.0,
            rnl,
        )

    @staticmethod
    def _validate_input(
        data: ET0Input,
    ) -> None:

        if not -90 <= data.latitude_deg <= 90:
            raise ValueError(
                "latitude_deg debe estar entre -90 y 90."
            )

        if data.elevation_m < -500:
            raise ValueError(
                "elevation_m contiene un valor no válido."
            )

        if (
            data.temperature_min_c
            >
            data.temperature_max_c
        ):
            raise ValueError(
                "temperature_min_c no puede superar "
                "temperature_max_c."
            )

        if not (
            0
            <= data.relative_humidity_pct
            <= 100
        ):
            raise ValueError(
                "relative_humidity_pct debe estar "
                "entre 0 y 100."
            )

        if (
            data.solar_radiation_mj_m2_day
            < 0
        ):
            raise ValueError(
                "La radiación solar no puede ser negativa."
            )

        if data.wind_speed_m_s < 0:
            raise ValueError(
                "La velocidad del viento no puede "
                "ser negativa."
            )