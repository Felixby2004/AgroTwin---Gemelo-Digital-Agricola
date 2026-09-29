from datetime import datetime
from typing import Any

from pydantic import (
    Field,
)

from api.schemas.common import (
    APIModel,
)


class UserRegisterRequest(
    APIModel
):

    email: str = Field(
        min_length=5,
        max_length=320,
    )

    full_name: str = Field(
        min_length=2,
        max_length=150,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserLoginRequest(
    APIModel
):

    email: str

    password: str


class UserRead(
    APIModel
):

    user_id: str

    email: str

    full_name: str

    system_role: str

    status: str

    created_at: datetime

    metadata: dict[
        str,
        Any
    ]


class TokenResponse(
    APIModel
):

    access_token: str

    token_type: str = "bearer"

    expires_in_minutes: int

    user: UserRead