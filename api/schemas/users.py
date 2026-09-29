from typing import Any, Literal

from pydantic import Field

from api.schemas.common import APIModel


SystemRoleValue = Literal[
    "ADMIN",
    "USER",
]


UserStatusValue = Literal[
    "ACTIVE",
    "DISABLED",
]


class UserAdminCreateRequest(
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

    system_role: SystemRoleValue = (
        "USER"
    )

    metadata: dict[
        str,
        Any
    ] = {}


class UserProfileUpdateRequest(
    APIModel
):

    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    metadata: dict[
        str,
        Any
    ] | None = None


class UserAdminUpdateRequest(
    APIModel
):

    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    system_role: SystemRoleValue | None = (
        None
    )

    status: UserStatusValue | None = (
        None
    )

    metadata: dict[
        str,
        Any
    ] | None = None
