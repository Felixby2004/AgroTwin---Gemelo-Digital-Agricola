from twin.identity import (
    SystemRole,
    ParcelRole,
    ParcelPermission,
)


class AuthorizationEngine:

    ROLE_PERMISSIONS = {

        ParcelRole.OWNER: {
            ParcelPermission.VIEW,
            ParcelPermission.EDIT,
            ParcelPermission.MANAGE_KNOWLEDGE,
            ParcelPermission.RUN_REASONING,
            ParcelPermission.RESPOND_RECOMMENDATION,
            ParcelPermission.MANAGE_GOVERNANCE,
            ParcelPermission.EXPORT_DATA,
            ParcelPermission.MANAGE_MEMBERS,
        },


        ParcelRole.FARMER: {
            ParcelPermission.VIEW,
            ParcelPermission.EDIT,
            ParcelPermission.MANAGE_KNOWLEDGE,
            ParcelPermission.RUN_REASONING,
            ParcelPermission.RESPOND_RECOMMENDATION,
        },


        ParcelRole.AGRONOMIST: {
            ParcelPermission.VIEW,
            ParcelPermission.EDIT,
            ParcelPermission.MANAGE_KNOWLEDGE,
            ParcelPermission.RUN_REASONING,
            ParcelPermission.RESPOND_RECOMMENDATION,
            ParcelPermission.EXPORT_DATA,
        },


        ParcelRole.VIEWER: {
            ParcelPermission.VIEW,
        },
    }


    def has_parcel_permission(
        self,
        *,
        system_role: SystemRole,
        parcel_role: ParcelRole | None,
        permission: ParcelPermission,
    ) -> bool:

        # Global administrators can operate
        # across every parcel.
        if (
            system_role
            == SystemRole.ADMIN
        ):
            return True


        if parcel_role is None:
            return False


        permissions = (
            self.ROLE_PERMISSIONS.get(
                parcel_role,
                set(),
            )
        )


        return (
            permission
            in permissions
        )


    def get_parcel_permissions(
        self,
        *,
        system_role: SystemRole,
        parcel_role: ParcelRole | None,
    ) -> set[
        ParcelPermission
    ]:

        if (
            system_role
            == SystemRole.ADMIN
        ):
            return set(
                ParcelPermission
            )


        if parcel_role is None:
            return set()


        return set(
            self.ROLE_PERMISSIONS.get(
                parcel_role,
                set(),
            )
        )
