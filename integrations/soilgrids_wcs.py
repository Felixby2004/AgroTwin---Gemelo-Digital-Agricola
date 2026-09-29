from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

import rasterio
import requests
from rasterio.warp import transform

from twin import (
    SoilLayer,
    SoilProfile,
)

class SoilGridsWCSError(Exception):
    """Error de acceso a SoilGrids mediante WCS."""


@dataclass
class SoilGridsWCSValue:
    property_name: str

    depth_top_cm: int
    depth_bottom_cm: int

    raw_value: float | None
    converted_value: float | None

    sampling_method: str
    distance_pixels: float | None = None


class SoilGridsWCSClient:

    BASE_URL_TEMPLATE = (
        "https://maps.isric.org/mapserv"
    )

    PROPERTY_CONFIG = {
        "sand": {
            "conversion_factor": 10.0,
        },
        "silt": {
            "conversion_factor": 10.0,
        },
        "clay": {
            "conversion_factor": 10.0,
        },
        "bdod": {
            "conversion_factor": 100.0,
        },
        "soc": {
            "conversion_factor": 10.0,
        },
        "phh2o": {
            "conversion_factor": 10.0,
        },
        "wv0033": {
            "conversion_factor": 10.0,
        },
        "wv1500": {
            "conversion_factor": 10.0,
        },
    }

    DEPTHS = [
        (0, 5),
        (5, 15),
        (15, 30),
        (30, 60),
        (60, 100),
        (100, 200),
    ]

    SOILGRIDS_CRS = (
        "+proj=igh "
        "+lat_0=0 "
        "+lon_0=0 "
        "+datum=WGS84 "
        "+units=m "
        "+no_defs"
    )

    def __init__(
        self,
        timeout_seconds: int = 60,
    ):
        self.timeout_seconds = timeout_seconds

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


    def describe_coverage(
        self,
        property_name: str,
        depth_top_cm: int,
        depth_bottom_cm: int,
    ) -> str:

        coverage_id = (
            f"{property_name}_"
            f"{depth_top_cm}-{depth_bottom_cm}cm_mean"
        )

        params = {
            "map": f"/map/{property_name}.map",
            "SERVICE": "WCS",
            "VERSION": "2.0.1",
            "REQUEST": "DescribeCoverage",
            "COVERAGEID": coverage_id,
        }

        try:
            response = requests.get(
                self.BASE_URL_TEMPLATE,
                params=params,
                timeout=self.timeout_seconds,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            raise SoilGridsWCSError(
                f"No fue posible describir {coverage_id}: {exc}"
            ) from exc

        return response.text

    def get_capabilities(
        self,
        property_name: str,
    ) -> str:

        if property_name not in self.PROPERTY_CONFIG:
            raise ValueError(
                f"Propiedad no soportada: {property_name}"
            )

        params = {
            "map": f"/map/{property_name}.map",
            "SERVICE": "WCS",
            "VERSION": "2.0.1",
            "REQUEST": "GetCapabilities",
        }

        try:
            response = requests.get(
                self.BASE_URL_TEMPLATE,
                params=params,
                timeout=self.timeout_seconds,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            raise SoilGridsWCSError(
                "No fue posible consultar "
                f"el WCS de SoilGrids: {exc}"
            ) from exc

        return response.text


    def get_value(
        self,
        property_name: str,
        depth_top_cm: int,
        depth_bottom_cm: int,
        latitude: float,
        longitude: float,
    ) -> SoilGridsWCSValue:

        self._validate_coordinates(
            latitude,
            longitude,
        )

        if property_name not in self.PROPERTY_CONFIG:
            raise ValueError(
                f"Propiedad no soportada: {property_name}"
            )

        coverage_id = (
            f"{property_name}_"
            f"{depth_top_cm}-{depth_bottom_cm}cm_mean"
        )

        # -------------------------------------------------
        # Transformar WGS84 -> SoilGrids Homolosine
        # -------------------------------------------------

        xs, ys = transform(
            "EPSG:4326",
            self.SOILGRIDS_CRS,
            [longitude],
            [latitude],
        )

        x = xs[0]
        y = ys[0]

        # Ventana de 2 km x 2 km.
        # SoilGrids tiene resolución aproximada de 250 m.
        buffer_m = 1000

        x_min = x - buffer_m
        x_max = x + buffer_m

        y_min = y - buffer_m
        y_max = y + buffer_m

        params = [
            (
                "map",
                f"/map/{property_name}.map",
            ),
            (
                "SERVICE",
                "WCS",
            ),
            (
                "VERSION",
                "2.0.1",
            ),
            (
                "REQUEST",
                "GetCoverage",
            ),
            (
                "COVERAGEID",
                coverage_id,
            ),
            (
                "FORMAT",
                "GEOTIFF_INT16",
            ),
            (
                "SUBSET",
                f"x({x_min},{x_max})",
            ),
            (
                "SUBSET",
                f"y({y_min},{y_max})",
            ),
            (
                "SUBSETTINGCRS",
                "http://www.opengis.net/def/crs/EPSG/0/152160",
            ),
            (
                "OUTPUTCRS",
                "http://www.opengis.net/def/crs/EPSG/0/152160",
            ),
        ]

        try:
            response = requests.get(
                self.BASE_URL_TEMPLATE,
                params=params,
                timeout=self.timeout_seconds,
            )

            response.raise_for_status()

        except requests.RequestException as exc:
            raise SoilGridsWCSError(
                f"No fue posible descargar "
                f"{coverage_id}: {exc}"
            ) from exc

        content_type = response.headers.get(
            "Content-Type",
            "",
        )

        if (
            "tiff" not in content_type.lower()
            and
            "octet-stream" not in content_type.lower()
        ):
            text_preview = response.text[:1000]

            raise SoilGridsWCSError(
                "La respuesta WCS no parece ser un GeoTIFF. "
                f"Content-Type={content_type}. "
                f"Respuesta: {text_preview}"
            )

        raw_value = None

        sampling_method = "NO_DATA"
        distance_pixels = None

        with TemporaryDirectory() as temp_dir:

            output_path = (
                Path(temp_dir)
                / f"{coverage_id}.tif"
            )

            output_path.write_bytes(
                response.content
            )

            try:
                with rasterio.open(
                    output_path
                ) as dataset:

                    band = dataset.read(1)

                    nodata = dataset.nodata

                    row, col = dataset.index(
                        x,
                        y,
                    )

                    # -----------------------------------------
                    # 1. Intentar usar el píxel exacto
                    # -----------------------------------------

                    if (
                        0 <= row < dataset.height
                        and
                        0 <= col < dataset.width
                    ):

                        candidate = float(
                            band[row, col]
                        )

                        is_valid = (
                            candidate > 0
                            and
                            (
                                nodata is None
                                or candidate != nodata
                            )
                        )

                        if is_valid:
                            raw_value = candidate

                            sampling_method = (
                                "EXACT_PIXEL"
                            )

                            distance_pixels = 0.0

                    # -----------------------------------------
                    # 2. Si el píxel exacto está vacío,
                    #    buscar el válido más cercano
                    # -----------------------------------------

                    if raw_value is None:

                        best_value = None
                        best_distance_squared = None

                        for r in range(
                            dataset.height
                        ):
                            for c in range(
                                dataset.width
                            ):

                                candidate = float(
                                    band[r, c]
                                )

                                if (
                                    nodata is not None
                                    and candidate == nodata
                                ):
                                    continue

                                if candidate <= 0:
                                    continue

                                distance_squared = (
                                    (r - row) ** 2
                                    +
                                    (c - col) ** 2
                                )

                                if (
                                    best_distance_squared
                                    is None
                                    or
                                    distance_squared
                                    <
                                    best_distance_squared
                                ):
                                    best_distance_squared = (
                                        distance_squared
                                    )

                                    best_value = (
                                        candidate
                                    )

                        if best_value is not None:

                            raw_value = best_value

                            sampling_method = (
                                "NEAREST_VALID_PIXEL"
                            )

                            distance_pixels = (
                                best_distance_squared
                                ** 0.5
                            )

            except rasterio.errors.RasterioIOError as exc:

                raise SoilGridsWCSError(
                    "La respuesta WCS no pudo abrirse "
                    "como GeoTIFF."
                ) from exc

        # -------------------------------------------------
        # Conversión de unidades SoilGrids
        # -------------------------------------------------

        if raw_value is None:

            converted_value = None

        else:

            factor = (
                self.PROPERTY_CONFIG[
                    property_name
                ][
                    "conversion_factor"
                ]
            )

            converted_value = (
                raw_value
                /
                factor
            )

        return SoilGridsWCSValue(
            property_name=property_name,
            depth_top_cm=depth_top_cm,
            depth_bottom_cm=depth_bottom_cm,
            raw_value=raw_value,
            converted_value=converted_value,
            sampling_method=sampling_method,
            distance_pixels=distance_pixels,
        )


    def get_soil_profile(
        self,
        latitude: float,
        longitude: float,
    ) -> SoilProfile:

        self._validate_coordinates(
            latitude,
            longitude,
        )

        layers_by_depth = {}

        for depth_top_cm, depth_bottom_cm in self.DEPTHS:

            depth_key = (
                depth_top_cm,
                depth_bottom_cm,
            )

            layers_by_depth[depth_key] = {
                "depth_top_cm": depth_top_cm,
                "depth_bottom_cm": depth_bottom_cm,
            }

            for property_name in self.PROPERTY_CONFIG:

                result = self.get_value(
                    property_name=property_name,
                    depth_top_cm=depth_top_cm,
                    depth_bottom_cm=depth_bottom_cm,
                    latitude=latitude,
                    longitude=longitude,
                )

                layers_by_depth[
                    depth_key
                ][property_name] = (
                    result.converted_value
                )

        layers = []

        for (
            depth_top_cm,
            depth_bottom_cm,
        ), values in layers_by_depth.items():
            
            layer = SoilLayer(
                depth_top_cm=depth_top_cm,
                depth_bottom_cm=depth_bottom_cm,

                sand_pct=values.get(
                    "sand"
                ),

                silt_pct=values.get(
                    "silt"
                ),

                clay_pct=values.get(
                    "clay"
                ),

                bulk_density_g_cm3=values.get(
                    "bdod"
                ),

                organic_carbon_g_kg=values.get(
                    "soc"
                ),

                ph_h2o=values.get(
                    "phh2o"
                ),

                water_content_33kpa_pct=values.get(
                    "wv0033"
                ),

                water_content_1500kpa_pct=values.get(
                    "wv1500"
                ),
            )

            layers.append(layer)

        return SoilProfile(
            latitude=latitude,
            longitude=longitude,
            source="SOILGRIDS_WCS",
            layers=layers,
        )