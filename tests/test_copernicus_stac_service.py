from services.copernicus_stac_service import (
    CopernicusSTACService,
)


def test_collection_name():

    service = (
        CopernicusSTACService()
    )

    assert (
        service.COLLECTION
        ==
        "sentinel-2-l2a"
    )