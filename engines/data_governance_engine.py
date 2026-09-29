from datetime import (
    datetime,
    timezone,
)

from twin.data_governance import (
    DataConsent,
    DataAccessRequest,
    DataAccessDecision,
)


class DataGovernanceEngine:

    def evaluate(
        self,
        request: DataAccessRequest,
        consents: list[
            DataConsent
        ],
        now: datetime | None = None,
    ) -> DataAccessDecision:

        if now is None:

            now = datetime.now(
                timezone.utc
            )


        # =================================================
        # 1. CONSENTS FOR PARCEL
        # =================================================

        parcel_consents = [
            consent
            for consent
            in consents
            if consent.parcel_id
            == request.parcel_id
        ]


        if not parcel_consents:

            return DataAccessDecision(
                allowed=False,

                reason=(
                    "No consent exists "
                    "for this parcel."
                ),
            )


        # =================================================
        # 2. ACTIVE CONSENTS
        # =================================================

        active_consents = [
            consent
            for consent
            in parcel_consents
            if consent.is_active(
                now
            )
        ]


        if not active_consents:

            return DataAccessDecision(
                allowed=False,

                reason=(
                    "No active consent exists "
                    "for this parcel."
                ),
            )


        # =================================================
        # 3. MATCH PURPOSE / PERMISSION / CATEGORY
        # =================================================

        for consent in active_consents:

            if (
                request.permission
                not in consent.permissions
            ):
                continue


            if (
                request.purpose
                not in consent.purposes
            ):
                continue


            if (
                request.data_category
                not in
                consent
                .allowed_data_categories
            ):
                continue


            return DataAccessDecision(
                allowed=True,

                reason=(
                    "Access permitted by "
                    "active consent."
                ),

                consent_id=(
                    consent.consent_id
                ),

                metadata={
                    "subject_id":
                        consent.subject_id
                },
            )


        # =================================================
        # 4. DENIED
        # =================================================

        return DataAccessDecision(
            allowed=False,

            reason=(
                "Requested operation is "
                "not permitted by active "
                "consent."
            ),
        )