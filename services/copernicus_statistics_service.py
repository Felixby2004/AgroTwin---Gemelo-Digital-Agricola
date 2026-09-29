from datetime import (
    datetime,
    timezone,
)

import httpx


from services.copernicus_auth_service import (
    CopernicusAuthService,
)

from services.copernicus_config import (
    CopernicusConfig,
)


class CopernicusStatisticsService:

    def __init__(
        self,
    ):

        self.auth = (
            CopernicusAuthService()
        )


    # =====================================================
    # SENTINEL HUB EVALSCRIPT
    # =====================================================

    EVALSCRIPT = """
//VERSION=3

function setup() {
    return {
        input: [{
            bands: [
                "B04",
                "B08",
                "B11",
                "SCL",
                "dataMask"
            ]
        }],

        output: [
            {
                id: "ndvi",
                bands: 1,
                sampleType: "FLOAT32"
            },
            {
                id: "ndmi",
                bands: 1,
                sampleType: "FLOAT32"
            },
            {
                id: "dataMask",
                bands: 1
            }
        ]
    };
}


function evaluatePixel(sample) {

    const invalidClasses = [
        0,   // No data
        1,   // Saturated / defective
        3,   // Cloud shadows
        8,   // Cloud medium probability
        9,   // Cloud high probability
        10,  // Thin cirrus
        11   // Snow / ice
    ];


    const valid = (
        sample.dataMask === 1
        &&
        !invalidClasses.includes(
            sample.SCL
        )
    );


    if (!valid) {

        return {
            ndvi: [0],
            ndmi: [0],
            dataMask: [0]
        };
    }


    const ndviDenominator =
        sample.B08
        + sample.B04;


    const ndmiDenominator =
        sample.B08
        + sample.B11;


    const ndvi = (
        ndviDenominator !== 0

        ? (
            sample.B08
            - sample.B04
        )
        / ndviDenominator

        : 0
    );


    const ndmi = (
        ndmiDenominator !== 0

        ? (
            sample.B08
            - sample.B11
        )
        / ndmiDenominator

        : 0
    );


    return {
        ndvi: [ndvi],
        ndmi: [ndmi],
        dataMask: [1]
    };
}
"""


    # =====================================================
    # GET INDICES
    # =====================================================

    def get_indices(
        self,
        *,
        geometry: dict,
        start_date: datetime,
        end_date: datetime,
        max_cloud_cover: float = 30.0,
        resolution_m: float = 10.0,
    ) -> dict:

        # =================================================
        # 1. VALIDATE GEOMETRY
        # =================================================

        self._validate_geometry(
            geometry
        )


        # =================================================
        # 2. VALIDATE DATES
        # =================================================

        start_date = (
            self._ensure_utc(
                start_date
            )
        )

        end_date = (
            self._ensure_utc(
                end_date
            )
        )


        if (
            start_date
            >= end_date
        ):

            raise ValueError(
                "start_date must be "
                "earlier than end_date."
            )


        # =================================================
        # 3. VALIDATE CLOUD COVER
        # =================================================

        if not (
            0.0
            <= max_cloud_cover
            <= 100.0
        ):

            raise ValueError(
                "max_cloud_cover must "
                "be between 0 and 100."
            )


        # =================================================
        # 4. VALIDATE RESOLUTION
        # =================================================

        if resolution_m <= 0:

            raise ValueError(
                "resolution_m must "
                "be greater than 0."
            )


        # =================================================
        # 5. AUTHENTICATION
        # =================================================

        token = (
            self.auth
            .get_access_token()
        )


        # =================================================
        # 6. RESOLUTION
        #
        # Parcel geometry is stored in EPSG:4326 /
        # CRS84 longitude-latitude coordinates.
        #
        # Statistical API resx/resy therefore use
        # coordinate units (degrees), not metres.
        #
        # Approximation:
        #
        # 1 degree latitude ~= 111,320 metres
        #
        # This is sufficient for our parcel-level
        # statistical sampling.
        # =================================================

        resolution_deg = (
            resolution_m
            / 111_320.0
        )


        # =================================================
        # 7. REQUEST PAYLOAD
        # =================================================

        payload = {

            "input": {

                "bounds": {

                    "geometry":
                        geometry,

                    "properties": {

                        "crs": (
                            "http://www.opengis.net/"
                            "def/crs/OGC/1.3/CRS84"
                        )
                    },
                },


                "data": [

                    {
                        "type":
                            "sentinel-2-l2a",

                        "dataFilter": {

                            "timeRange": {

                                "from":
                                    start_date
                                    .isoformat(),

                                "to":
                                    end_date
                                    .isoformat(),
                            },


                            "maxCloudCoverage":
                                max_cloud_cover,


                            "mosaickingOrder":
                                "leastCC",
                        },
                    }
                ],
            },


            "aggregation": {

                "timeRange": {

                    "from":
                        start_date
                        .isoformat(),

                    "to":
                        end_date
                        .isoformat(),
                },


                "aggregationInterval": {

                    "of":
                        "P1D",
                },


                "lastIntervalBehavior":
                    "SHORTEN",


                "resx":
                    resolution_deg,


                "resy":
                    resolution_deg,


                "evalscript":
                    self.EVALSCRIPT,
            },
        }


        # =================================================
        # 8. REQUEST
        # =================================================

        response = (
            httpx.post(

                CopernicusConfig
                .STATISTICS_URL,

                headers={

                    "Authorization":
                        f"Bearer {token}",

                    "Content-Type":
                        "application/json",

                    "Accept":
                        "application/json",
                },

                json=payload,

                timeout=60.0,
            )
        )


        # =================================================
        # 9. ERROR DETAIL
        # =================================================

        if response.is_error:

            raise RuntimeError(
                "Copernicus Statistical API error "
                f"{response.status_code}: "
                f"{response.text}"
            )


        # =================================================
        # 10. RESPONSE
        # =================================================

        data = (
            response.json()
        )


        return (
            self._extract_latest(
                data
            )
        )


    # =====================================================
    # EXTRACT LATEST VALID INTERVAL
    # =====================================================

    def _extract_latest(
        self,
        response: dict,
    ) -> dict:

        intervals = (
            response.get(
                "data",
                [],
            )
        )


        valid_results = []


        for item in intervals:

            try:

                ndvi_stats = (
                    item[
                        "outputs"
                    ][
                        "ndvi"
                    ][
                        "bands"
                    ][
                        "B0"
                    ][
                        "stats"
                    ]
                )


                ndmi_stats = (
                    item[
                        "outputs"
                    ][
                        "ndmi"
                    ][
                        "bands"
                    ][
                        "B0"
                    ][
                        "stats"
                    ]
                )

            except (
                KeyError,
                TypeError,
            ):

                continue


            # =================================================
            # COUNTS
            # =================================================

            sample_count = int(
                ndvi_stats.get(
                    "sampleCount",
                    0,
                )
                or 0
            )


            no_data_count = int(
                ndvi_stats.get(
                    "noDataCount",
                    0,
                )
                or 0
            )


            valid_pixels = max(
                0,
                sample_count
                - no_data_count,
            )


            if valid_pixels <= 0:

                continue


            # =================================================
            # VALID FRACTION
            # =================================================

            valid_fraction = (
                valid_pixels
                / sample_count

                if sample_count
                else 0.0
            )


            # =================================================
            # MEANS MUST EXIST
            # =================================================

            ndvi_mean = (
                ndvi_stats.get(
                    "mean"
                )
            )

            ndmi_mean = (
                ndmi_stats.get(
                    "mean"
                )
            )


            if (
                ndvi_mean is None
                or
                ndmi_mean is None
            ):

                continue


            # =================================================
            # STORE VALID RESULT
            # =================================================

            valid_results.append(
                {

                    "interval":
                        item.get(
                            "interval"
                        ),


                    # -----------------------------------------
                    # NDVI
                    # -----------------------------------------

                    "ndvi_mean":
                        ndvi_mean,

                    "ndvi_min":
                        ndvi_stats.get(
                            "min"
                        ),

                    "ndvi_max":
                        ndvi_stats.get(
                            "max"
                        ),

                    "ndvi_std":
                        ndvi_stats.get(
                            "stDev"
                        ),


                    # -----------------------------------------
                    # NDMI
                    # -----------------------------------------

                    "ndmi_mean":
                        ndmi_mean,

                    "ndmi_min":
                        ndmi_stats.get(
                            "min"
                        ),

                    "ndmi_max":
                        ndmi_stats.get(
                            "max"
                        ),

                    "ndmi_std":
                        ndmi_stats.get(
                            "stDev"
                        ),


                    # -----------------------------------------
                    # COVERAGE
                    # -----------------------------------------

                    "sample_count":
                        sample_count,

                    "no_data_count":
                        no_data_count,

                    "valid_pixel_count":
                        valid_pixels,

                    "valid_fraction":
                        round(
                            valid_fraction,
                            6,
                        ),
                }
            )


        # =================================================
        # NO VALID DATA
        # =================================================

        if not valid_results:

            raise ValueError(
                "No valid Sentinel-2 "
                "pixels were found for "
                "the requested parcel "
                "and period."
            )


        # =================================================
        # NEWEST INTERVAL FIRST
        # =================================================

        valid_results.sort(
            key=lambda result: (
                (
                    result.get(
                        "interval"
                    )
                    or {}
                ).get(
                    "from",
                    "",
                )
            ),
            reverse=True,
        )


        return (
            valid_results[
                0
            ]
        )


    # =====================================================
    # GEOMETRY VALIDATION
    # =====================================================

    @staticmethod
    def _validate_geometry(
        geometry: dict,
    ) -> None:

        if not isinstance(
            geometry,
            dict,
        ):

            raise ValueError(
                "geometry must be "
                "a GeoJSON object."
            )


        geometry_type = (
            geometry.get(
                "type"
            )
        )


        if geometry_type not in {
            "Polygon",
            "MultiPolygon",
        }:

            raise ValueError(
                "Parcel geometry must "
                "be Polygon or MultiPolygon."
            )


        coordinates = (
            geometry.get(
                "coordinates"
            )
        )


        if not coordinates:

            raise ValueError(
                "Parcel geometry has "
                "no coordinates."
            )


    # =====================================================
    # UTC NORMALIZATION
    # =====================================================

    @staticmethod
    def _ensure_utc(
        value: datetime,
    ) -> datetime:

        if value.tzinfo is None:

            return value.replace(
                tzinfo=timezone.utc
            )


        return value.astimezone(
            timezone.utc
        )