from datetime import (
    datetime,
    timezone,
)

from uuid import uuid4


class Sentinel2Service:

    # Cloud thresholds are operational
    # defaults and can later become
    # configurable per project.

    HIGH_QUALITY_CLOUD_MAX = 10.0

    ACCEPTABLE_CLOUD_MAX = 30.0

    STALE_DAYS = 10


    def calculate_ndvi(
        self,
        red: float,
        nir: float,
    ) -> float:

        denominator = (
            nir + red
        )

        if denominator == 0:

            raise ValueError(
                "Cannot calculate NDVI: "
                "NIR + RED = 0."
            )

        value = (
            nir - red
        ) / denominator

        return round(
            value,
            6,
        )


    def calculate_ndmi(
        self,
        nir: float,
        swir: float,
    ) -> float:

        denominator = (
            nir + swir
        )

        if denominator == 0:

            raise ValueError(
                "Cannot calculate NDMI: "
                "NIR + SWIR = 0."
            )

        value = (
            nir - swir
        ) / denominator

        return round(
            value,
            6,
        )


    def quality_from_clouds(
        self,
        cloud_cover_pct: float,
    ) -> float:

        if (
            cloud_cover_pct
            <= self.HIGH_QUALITY_CLOUD_MAX
        ):
            return 0.95

        if (
            cloud_cover_pct
            <= self.ACCEPTABLE_CLOUD_MAX
        ):
            return 0.75

        if cloud_cover_pct <= 60.0:
            return 0.50

        return 0.25


    def determine_status(
        self,
        acquired_at: datetime,
        now: datetime | None = None,
    ) -> str:

        if now is None:
            now = datetime.now(
                timezone.utc
            )

        if acquired_at.tzinfo is None:

            acquired_at = (
                acquired_at.replace(
                    tzinfo=timezone.utc
                )
            )

        else:

            acquired_at = (
                acquired_at.astimezone(
                    timezone.utc
                )
            )

        age_days = (
            now - acquired_at
        ).total_seconds() / 86400.0

        if (
            age_days
            > self.STALE_DAYS
        ):
            return "STALE"

        return "ACTIVE"


    def build_evidence(
        self,
        *,
        parcel_id: str,
        scene_id: str,
        acquired_at: datetime,
        red: float,
        nir: float,
        swir: float,
        cloud_cover_pct: float,
        source_url: str | None,
        processing_level: str,
        metadata: dict | None = None,
        now: datetime | None = None,
    ) -> list[dict]:

        ndvi = self.calculate_ndvi(
            red=red,
            nir=nir,
        )

        ndmi = self.calculate_ndmi(
            nir=nir,
            swir=swir,
        )

        quality_score = (
            self.quality_from_clouds(
                cloud_cover_pct
            )
        )

        status = (
            self.determine_status(
                acquired_at=acquired_at,
                now=now,
            )
        )


        provenance_base = {
            "source_type":
                "EXTERNAL",

            "source_name":
                "SENTINEL_2",

            "source_id":
                scene_id,

            "source_version":
                processing_level,

            "generated_at":
                acquired_at.isoformat(),

            "valid_at":
                acquired_at.isoformat(),

            "spatial_scope": {
                "parcel_id":
                    parcel_id
            },

            "transformation":
                (
                    "Vegetation index derived "
                    "from Sentinel-2 spectral bands."
                ),

            "parent_ids": [],

            "metadata": {
                "cloud_cover_pct":
                    cloud_cover_pct,

                "source_url":
                    source_url,

                "processing_level":
                    processing_level,

                **(
                    metadata
                    or {}
                ),
            },
        }


        ndvi_evidence = {
            "evidence_id":
                (
                    "EV-S2-NDVI-"
                    + uuid4().hex[
                        :10
                    ].upper()
                ),

            "parcel_id":
                parcel_id,

            "variable":
                "ndvi",

            "value":
                ndvi,

            "unit":
                "index",

            "observed_at":
                acquired_at,

            "status":
                status,

            "quality_score":
                quality_score,

            "uncertainty":
                None,

            "provenance":
                {
                    **provenance_base,

                    "transformation":
                        (
                            "NDVI = "
                            "(B08 - B04) / "
                            "(B08 + B04)"
                        ),
                },

            "metadata": {
                "scene_id":
                    scene_id,

                "satellite":
                    "Sentinel-2",

                "index":
                    "NDVI",

                "cloud_cover_pct":
                    cloud_cover_pct,
            },
        }


        ndmi_evidence = {
            "evidence_id":
                (
                    "EV-S2-NDMI-"
                    + uuid4().hex[
                        :10
                    ].upper()
                ),

            "parcel_id":
                parcel_id,

            "variable":
                "ndmi",

            "value":
                ndmi,

            "unit":
                "index",

            "observed_at":
                acquired_at,

            "status":
                status,

            "quality_score":
                quality_score,

            "uncertainty":
                None,

            "provenance":
                {
                    **provenance_base,

                    "transformation":
                        (
                            "NDMI = "
                            "(B08 - B11) / "
                            "(B08 + B11)"
                        ),
                },

            "metadata": {
                "scene_id":
                    scene_id,

                "satellite":
                    "Sentinel-2",

                "index":
                    "NDMI",

                "cloud_cover_pct":
                    cloud_cover_pct,
            },
        }


        return [
            ndvi_evidence,
            ndmi_evidence,
        ]