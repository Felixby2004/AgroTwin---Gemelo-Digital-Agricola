from datetime import (
    datetime,
    timedelta,
    timezone,
)

import httpx


from services.copernicus_config import (
    CopernicusConfig,
)


class CopernicusAuthService:

    def __init__(self):

        self._access_token = None

        self._expires_at = None


    def get_access_token(
        self,
    ) -> str:

        if (
            self._access_token
            and self._expires_at
            and datetime.now(
                timezone.utc
            )
            < self._expires_at
        ):
            return self._access_token


        if (
            not CopernicusConfig.CLIENT_ID
            or
            not CopernicusConfig.CLIENT_SECRET
        ):
            raise RuntimeError(
                "CDSE_CLIENT_ID and "
                "CDSE_CLIENT_SECRET "
                "must be configured."
            )


        response = httpx.post(
            CopernicusConfig.TOKEN_URL,

            data={
                "grant_type":
                    "client_credentials",

                "client_id":
                    CopernicusConfig
                    .CLIENT_ID,

                "client_secret":
                    CopernicusConfig
                    .CLIENT_SECRET,
            },

            timeout=30.0,
        )


        response.raise_for_status()

        data = response.json()


        token = data.get(
            "access_token"
        )

        expires_in = int(
            data.get(
                "expires_in",
                300,
            )
        )


        if not token:
            raise RuntimeError(
                "Copernicus did not "
                "return an access token."
            )


        self._access_token = token

        self._expires_at = (
            datetime.now(
                timezone.utc
            )
            +
            timedelta(
                seconds=max(
                    30,
                    expires_in - 60,
                )
            )
        )


        return token