from datetime import (
    datetime,
    timedelta,
    timezone,
)

import jwt

from jwt import (
    InvalidTokenError,
)

from config.settings import (
    settings,
)


class TokenService:

    def create_access_token(
        self,
        *,
        user_id: str,
        email: str,
        system_role: str,
    ) -> str:

        now = datetime.now(
            timezone.utc
        )

        expires_at = (
            now
            + timedelta(
                minutes=(
                    settings
                    .jwt_access_token_minutes
                )
            )
        )


        payload = {
            "sub": user_id,
            "email": email,
            "system_role":
                system_role,
            "type":
                "access",
            "iat":
                now,
            "exp":
                expires_at,
        }


        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=(
                settings
                .jwt_algorithm
            ),
        )


    def decode_access_token(
        self,
        token: str,
    ) -> dict:

        try:

            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[
                    settings
                    .jwt_algorithm
                ],
            )

        except InvalidTokenError as exc:

            raise ValueError(
                "Invalid or expired "
                "access token."
            ) from exc


        if (
            payload.get(
                "type"
            )
            != "access"
        ):

            raise ValueError(
                "Invalid token type."
            )


        if not payload.get(
            "sub"
        ):

            raise ValueError(
                "Token has no subject."
            )


        return payload