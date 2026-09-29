import os

from dotenv import load_dotenv


load_dotenv()


class CopernicusConfig:

    CLIENT_ID = os.getenv(
        "CDSE_CLIENT_ID",
        "",
    )

    CLIENT_SECRET = os.getenv(
        "CDSE_CLIENT_SECRET",
        "",
    )

    STAC_URL = os.getenv(
        "CDSE_STAC_URL",
        "https://stac.dataspace.copernicus.eu/v1",
    )

    TOKEN_URL = os.getenv(
        "CDSE_TOKEN_URL",
        (
            "https://identity.dataspace.copernicus.eu/"
            "auth/realms/CDSE/protocol/"
            "openid-connect/token"
        ),
    )

    STATISTICS_URL = os.getenv(
        "CDSE_STATISTICS_URL",
        (
            "https://sh.dataspace.copernicus.eu/"
            "statistics/v1"
        ),
    )