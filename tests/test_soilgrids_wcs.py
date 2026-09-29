from integrations.soilgrids_wcs import (
    SoilGridsWCSClient,
)


def test_soilgrids_depths():

    assert SoilGridsWCSClient.DEPTHS == [
        (0, 5),
        (5, 15),
        (15, 30),
        (30, 60),
        (60, 100),
        (100, 200),
    ]


def test_soilgrids_has_six_depths():

    assert len(
        SoilGridsWCSClient.DEPTHS
    ) == 6