from engines.authorization_engine import (
    AuthorizationEngine,
)

from twin.identity import (
    SystemRole,
    ParcelRole,
    ParcelPermission,
)


engine = AuthorizationEngine()


def test_owner_has_governance_permission():

    allowed = (
        engine.has_parcel_permission(
            system_role=(
                SystemRole.USER
            ),
            parcel_role=(
                ParcelRole.OWNER
            ),
            permission=(
                ParcelPermission
                .MANAGE_GOVERNANCE
            ),
        )
    )

    assert allowed is True


def test_viewer_cannot_edit():

    allowed = (
        engine.has_parcel_permission(
            system_role=(
                SystemRole.USER
            ),
            parcel_role=(
                ParcelRole.VIEWER
            ),
            permission=(
                ParcelPermission.EDIT
            ),
        )
    )

    assert allowed is False


def test_admin_bypasses_parcel_membership():

    allowed = (
        engine.has_parcel_permission(
            system_role=(
                SystemRole.ADMIN
            ),
            parcel_role=None,
            permission=(
                ParcelPermission
                .MANAGE_GOVERNANCE
            ),
        )
    )

    assert allowed is True