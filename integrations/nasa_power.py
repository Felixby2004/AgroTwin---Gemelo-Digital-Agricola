from datetime import date, datetime

import requests

from twin import WeatherState

from engines.et0 import (
    ET0Calculator,
    ET0Input,
)


class NASAPowerError(Exception):
    """Error específico de integración con NASA POWER."""


class NASAPowerClient:

    BASE_URL = (
        "https://power.larc.nasa.gov/api/temporal/daily/point"
    )

    PARAMETERS = [
        "T2M",
        "T2M_MIN",
        "T2M_MAX",
        "RH2M",
        "PRECTOTCORR",
        "WS2M",
        "ALLSKY_SFC_SW_DWN",
    ]

    def __init__(
        self,
        timeout_seconds: int = 30,
    ):
        self.timeout_seconds = timeout_seconds

    def get_daily_weather(
        self,
        latitude: float,
        longitude: float,
        start_date: date,
        end_date: date,
    ) -> list[WeatherState]:

        self._validate_coordinates(
            latitude,
            longitude,
        )

        if start_date > end_date:
            raise ValueError(
                "start_date no puede ser posterior a end_date."
            )

        params = {
            "parameters": ",".join(
                self.PARAMETERS
            ),
            "community": "AG",
            "longitude": longitude,
            "latitude": latitude,
            "start": start_date.strftime(
                "%Y%m%d"
            ),
            "end": end_date.strftime(
                "%Y%m%d"
            ),
            "format": "JSON",
        }

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout_seconds,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            raise NASAPowerError(
                f"No fue posible consultar NASA POWER: {exc}"
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise NASAPowerError(
                "NASA POWER devolvió una respuesta JSON inválida."
            ) from exc

        return self._parse_daily_response(
            payload
        )

    def _parse_daily_response(
        self,
        payload: dict,
    ) -> list[WeatherState]:

        try:
            parameters = (
                payload["properties"]["parameter"]
            )
        except KeyError as exc:
            raise NASAPowerError(
                "La respuesta de NASA POWER no contiene "
                "la estructura esperada."
            ) from exc

        temperatures = parameters.get(
            "T2M",
            {},
        )

        weather_states = []

        for date_key in sorted(
            temperatures.keys()
        ):

            temperature = self._clean_value(
                parameters,
                "T2M",
                date_key,
            )

            if temperature is None:
                continue

            timestamp = datetime.strptime(
                date_key,
                "%Y%m%d",
            )

            weather_state = WeatherState(
                timestamp=timestamp,

                temperature_c=temperature,

                temperature_min_c=(
                    self._clean_value(
                        parameters,
                        "T2M_MIN",
                        date_key,
                    )
                ),

                temperature_max_c=(
                    self._clean_value(
                        parameters,
                        "T2M_MAX",
                        date_key,
                    )
                ),

                relative_humidity_pct=(
                    self._clean_value(
                        parameters,
                        "RH2M",
                        date_key,
                    )
                    or 0.0
                ),

                rainfall_mm=(
                    self._clean_value(
                        parameters,
                        "PRECTOTCORR",
                        date_key,
                    )
                    or 0.0
                ),

                wind_speed_m_s=(
                    self._clean_value(
                        parameters,
                        "WS2M",
                        date_key,
                    )
                ),

                solar_radiation_mj_m2_day=(
                    self._clean_value(
                        parameters,
                        "ALLSKY_SFC_SW_DWN",
                        date_key,
                    )
                ),

                et0_mm_day=None,

                source="NASA_POWER",
            )

            weather_states.append(
                weather_state
            )

        if not weather_states:
            raise NASAPowerError(
                "NASA POWER no devolvió datos meteorológicos válidos."
            )

        return weather_states

    def _clean_value(
        self,
        parameters: dict,
        parameter_name: str,
        date_key: str,
    ) -> float | None:

        parameter = parameters.get(
            parameter_name,
            {}
        )

        value = parameter.get(
            date_key
        )

        if value is None:
            return None

        # NASA POWER utiliza valores sentinel
        # para datos ausentes.
        if value <= -900:
            return None

        return float(value)

    def _validate_coordinates(
        self,
        latitude: float,
        longitude: float,
    ) -> None:

        if not -90 <= latitude <= 90:
            raise ValueError(
                "latitude debe estar entre -90 y 90."
            )

        if not -180 <= longitude <= 180:
            raise ValueError(
                "longitude debe estar entre -180 y 180."
            )


    def add_et0(
        self,
        weather_series: list[WeatherState],
        latitude: float,
        elevation_m: float,
    ) -> list[WeatherState]:

        calculator = ET0Calculator()

        enriched_weather = []

        for weather in weather_series:

            if (
                weather.temperature_min_c
                is None
                or
                weather.temperature_max_c
                is None
                or
                weather.solar_radiation_mj_m2_day
                is None
                or
                weather.wind_speed_m_s
                is None
            ):
                enriched_weather.append(
                    weather.model_copy(
                        update={
                            "quality_flag": (
                                "ET0_NOT_AVAILABLE"
                            )
                        }
                    )
                )

                continue

            et0_input = ET0Input(
                calculation_date=(
                    weather.timestamp.date()
                ),

                latitude_deg=latitude,

                elevation_m=elevation_m,

                temperature_mean_c=(
                    weather.temperature_c
                ),

                temperature_min_c=(
                    weather.temperature_min_c
                ),

                temperature_max_c=(
                    weather.temperature_max_c
                ),

                relative_humidity_pct=(
                    weather.relative_humidity_pct
                ),

                solar_radiation_mj_m2_day=(
                    weather.solar_radiation_mj_m2_day
                ),

                wind_speed_m_s=(
                    weather.wind_speed_m_s
                ),
            )

            et0_result = (
                calculator.calculate(
                    et0_input
                )
            )

            enriched_weather.append(
                weather.model_copy(
                    update={
                        "et0_mm_day": (
                            et0_result.et0_mm_day
                        ),
                        "quality_flag": (
                            "ET0_FAO56_ESTIMATED"
                        ),
                    }
                )
            )

        return enriched_weather