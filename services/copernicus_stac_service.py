from datetime import (
    datetime,
)

import httpx

from services.copernicus_config import (
    CopernicusConfig,
)


class CopernicusSTACService:

    COLLECTION = (
        "sentinel-2-l2a"
    )


    def search_sentinel2(
        self,
        *,
        bbox: list[float],
        start_date: datetime,
        end_date: datetime,
        max_cloud_cover: float = 30.0,
        limit: int = 10,
    ) -> list[dict]:

        if len(bbox) != 4:
            raise ValueError(
                "bbox must contain "
                "[min_lon, min_lat, "
                "max_lon, max_lat]."
            )


        url = (
            f"{CopernicusConfig.STAC_URL}"
            "/search"
        )


        payload = {
            "collections": [
                self.COLLECTION
            ],

            "bbox":
                bbox,

            "datetime": (
                f"{start_date.isoformat()}"
                f"/{end_date.isoformat()}"
            ),

            "query": {
                "eo:cloud_cover": {
                    "lte":
                        max_cloud_cover
                }
            },

            "limit":
                limit,

            "sortby": [
                {
                    "field":
                        "properties.datetime",

                    "direction":
                        "desc",
                }
            ],
        }


        with httpx.Client(
            timeout=30.0
        ) as client:

            response = client.post(
                url,
                json=payload,
            )

            response.raise_for_status()

            data = response.json()


        features = (
            data.get(
                "features",
                [],
            )
        )


        results = []

        for item in features:

            properties = (
                item.get(
                    "properties",
                    {},
                )
            )


            results.append(
                {
                    "scene_id":
                        item.get("id"),

                    "collection":
                        item.get(
                            "collection"
                        ),

                    "datetime":
                        properties.get(
                            "datetime"
                        ),

                    "cloud_cover_pct":
                        properties.get(
                            "eo:cloud_cover"
                        ),

                    "bbox":
                        item.get("bbox"),

                    "geometry":
                        item.get(
                            "geometry"
                        ),

                    "assets":
                        item.get(
                            "assets",
                            {},
                        ),
                }
            )


        return results