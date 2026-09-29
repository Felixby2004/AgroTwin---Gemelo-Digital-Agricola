import requests

from twin import SoilLayer, SoilProfile


class SoilGridsError(Exception):
    """Error específico de integración con SoilGrids."""


class SoilGridsClient:

    BASE_URL = (
        "https://rest.isric.org/"
        "soilgrids/v2.0/properties/query"
    )

    PROPERTIES = [
        "sand",
        "silt",
        "clay",
        "bdod",
        "soc",
        "phh2o",
    ]

    DEPTHS = [
        "0-5cm",
        "5-15cm",
        "15-30cm",
    ]

    def __init__(
        self,
        timeout_seconds: int = 30,
    ):
        self.timeout_seconds = timeout_seconds

    def get_soil_profile(
        self,
        latitude: float,
        longitude: float,
    ) -> SoilProfile:

        self._validate_coordinates(
            latitude,
            longitude,
        )

        params = [
            ("lon", longitude),
            ("lat", latitude),
        ]

        for prop in self.PROPERTIES:
            params.append(
                ("property", prop)
            )

        for depth in self.DEPTHS:
            params.append(
                ("depth", depth)
            )

        params.append(
            ("value", "mean")
        )

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout_seconds,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            raise SoilGridsError(
                "No fue posible consultar SoilGrids. "
                "La API REST puede estar temporalmente "
                f"no disponible: {exc}"
            ) from exc

        try:
            payload = response.json()

        except ValueError as exc:
            raise SoilGridsError(
                "SoilGrids devolvió JSON inválido."
            ) from exc

        return self._parse_response(
            payload=payload,
            latitude=latitude,
            longitude=longitude,
        )

    def _parse_response(
        self,
        payload: dict,
        latitude: float,
        longitude: float,
    ) -> SoilProfile:

        properties = payload.get(
            "properties",
            {}
        )

        layers_raw = properties.get(
            "layers",
            []
        )

        if not layers_raw:
            raise SoilGridsError(
                "SoilGrids no devolvió capas de suelo."
            )

        depth_map = {}

        for property_layer in layers_raw:

            property_name = (
                property_layer.get("name")
            )

            depths = (
                property_layer.get("depths", [])
            )

            for depth in depths:

                values = depth.get("values", {})

                mean_value = values.get("mean")

                if mean_value is None:
                    continue

                label = depth.get("label")

                if not label:
                    range_data = depth.get("range", {})

                    top_depth = range_data.get("top_depth")
                    bottom_depth = range_data.get("bottom_depth")

                    if (
                        top_depth is not None
                        and bottom_depth is not None
                    ):
                        label = (
                            f"{int(top_depth)}-"
                            f"{int(bottom_depth)}cm"
                        )

                if not label:
                    continue

                label = self._normalize_depth_label(
                    label
                )

                if label not in depth_map:
                    depth_map[label] = {}

                depth_map[label][property_name] = (
                    mean_value
                )

        layers = []

        for depth_label in self.DEPTHS:

            normalized_depth = (
                self._normalize_depth_label(
                    depth_label
                )
            )

            raw = depth_map.get(
                normalized_depth
            )

            if raw is None:
                continue

            top_cm, bottom_cm = (
                self._parse_depth_label(
                    normalized_depth
                )
            )

            layer = SoilLayer(
                depth_top_cm=top_cm,
                depth_bottom_cm=bottom_cm,

                sand_pct=(
                    self._convert_texture(
                        raw.get("sand")
                    )
                ),

                silt_pct=(
                    self._convert_texture(
                        raw.get("silt")
                    )
                ),

                clay_pct=(
                    self._convert_texture(
                        raw.get("clay")
                    )
                ),

                bulk_density_g_cm3=(
                    self._convert_bulk_density(
                        raw.get("bdod")
                    )
                ),

                organic_carbon_g_kg=(
                    self._convert_soc(
                        raw.get("soc")
                    )
                ),

                ph_h2o=(
                    self._convert_ph(
                        raw.get("phh2o")
                    )
                ),

                water_content_33kpa_pct=values.get(
                    "wv0033"
                ),

                water_content_1500kpa_pct=values.get(
                    "wv1500"
                ),
            )

            layers.append(layer)


        if not layers:
            raise SoilGridsError(
                "SoilGrids REST respondió correctamente, "
                "pero no devolvió valores numéricos para "
                "las propiedades y profundidades solicitadas."
            )

        return SoilProfile(
            latitude=latitude,
            longitude=longitude,
            layers=layers,
        )

    @staticmethod
    def _convert_texture(
        value: float | None,
    ) -> float | None:

        if value is None:
            return None

        # SoilGrids: g/kg
        # /10 -> %
        return float(value) / 10

    @staticmethod
    def _convert_bulk_density(
        value: float | None,
    ) -> float | None:

        if value is None:
            return None

        # cg/cm3 /100 -> g/cm3
        return float(value) / 100

    @staticmethod
    def _convert_soc(
        value: float | None,
    ) -> float | None:

        if value is None:
            return None

        # dg/kg /10 -> g/kg
        return float(value) / 10

    @staticmethod
    def _convert_ph(
        value: float | None,
    ) -> float | None:

        if value is None:
            return None

        return float(value) / 10

    @staticmethod
    def _parse_depth_label(
        depth_label: str,
    ) -> tuple[int, int]:

        clean = depth_label.replace(
            "cm",
            "",
        )

        top, bottom = clean.split("-")

        return int(top), int(bottom)

    @staticmethod
    def _validate_coordinates(
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

    @staticmethod
    def _normalize_depth_label(
        label: str,
    ) -> str:

        normalized = (
            str(label)
            .strip()
            .lower()
            .replace(" ", "")
            .replace("_", "-")
        )

        if not normalized.endswith("cm"):
            normalized += "cm"

        return normalized