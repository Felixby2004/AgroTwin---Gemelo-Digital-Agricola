from dataclasses import (
    dataclass,
    field,
)

from datetime import datetime
from enum import Enum
from typing import Any


class UserStatus(
    str,
    Enum,
):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class SystemRole(
    str,
    Enum,
):
    ADMIN = "ADMIN"
    USER = "USER"


class ParcelRole(
    str,
    Enum,
):
    OWNER = "OWNER"
    FARMER = "FARMER"
    AGRONOMIST = "AGRONOMIST"
    VIEWER = "VIEWER"


class ParcelPermission(
    str,
    Enum,
):
    VIEW = "VIEW"
    EDIT = "EDIT"
    MANAGE_KNOWLEDGE = "MANAGE_KNOWLEDGE"
    RUN_REASONING = "RUN_REASONING"
    RESPOND_RECOMMENDATION = (
        "RESPOND_RECOMMENDATION"
    )
    MANAGE_GOVERNANCE = (
        "MANAGE_GOVERNANCE"
    )
    EXPORT_DATA = "EXPORT_DATA"
    MANAGE_MEMBERS = "MANAGE_MEMBERS"


@dataclass
class UserIdentity:

    user_id: str

    email: str

    full_name: str

    system_role: SystemRole

    status: UserStatus

    created_at: datetime

    metadata: dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )


@dataclass
class ParcelMembership:

    membership_id: str

    parcel_id: str

    user_id: str

    role: ParcelRole

    created_at: datetime

    metadata: dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )