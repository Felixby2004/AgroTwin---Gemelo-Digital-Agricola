from datetime import (
    datetime,
    timezone,
    timedelta,
)


from twin.data_governance import (
    DataConsent,
    DataPurpose,
    DataPermission,
    ConsentStatus,
    DataAccessRequest,
)

from engines.data_governance_engine import (
    DataGovernanceEngine,
)


engine = (
    DataGovernanceEngine()
)


def build_consent():

    return DataConsent(
        consent_id="CONSENT-001",

        parcel_id="PARCEL-001",

        subject_id="FARMER-001",

        purposes=[
            DataPurpose
            .DIGITAL_TWIN_OPERATION,

            DataPurpose
            .RECOMMENDATION,
        ],

        permissions=[
            DataPermission.READ,
            DataPermission.PROCESS,
        ],

        allowed_data_categories=[
            "MACHINE_EVIDENCE",
            "FARMER_KNOWLEDGE",
        ],

        created_at=(
            datetime.now(
                timezone.utc
            )
        ),

        status=(
            ConsentStatus.ACTIVE
        ),
    )


def test_allowed_processing():

    consent = build_consent()


    request = DataAccessRequest(
        actor_id="SYSTEM",

        parcel_id="PARCEL-001",

        permission=(
            DataPermission.PROCESS
        ),

        purpose=(
            DataPurpose
            .DIGITAL_TWIN_OPERATION
        ),

        data_category=(
            "MACHINE_EVIDENCE"
        ),
    )


    result = engine.evaluate(
        request=request,
        consents=[
            consent
        ],
    )


    assert result.allowed is True

    assert (
        result.consent_id
        ==
        "CONSENT-001"
    )


def test_export_is_denied():

    consent = build_consent()


    request = DataAccessRequest(
        actor_id="SYSTEM",

        parcel_id="PARCEL-001",

        permission=(
            DataPermission.EXPORT
        ),

        purpose=(
            DataPurpose.EXPORT
        ),

        data_category=(
            "MACHINE_EVIDENCE"
        ),
    )


    result = engine.evaluate(
        request=request,
        consents=[
            consent
        ],
    )


    assert result.allowed is False


def test_revoked_consent_is_denied():

    consent = build_consent()

    consent.status = (
        ConsentStatus.REVOKED
    )


    request = DataAccessRequest(
        actor_id="SYSTEM",

        parcel_id="PARCEL-001",

        permission=(
            DataPermission.PROCESS
        ),

        purpose=(
            DataPurpose
            .DIGITAL_TWIN_OPERATION
        ),

        data_category=(
            "MACHINE_EVIDENCE"
        ),
    )


    result = engine.evaluate(
        request=request,
        consents=[
            consent
        ],
    )


    assert result.allowed is False


def test_expired_consent_is_denied():

    consent = build_consent()

    consent.valid_until = (
        datetime.now(
            timezone.utc
        )
        -
        timedelta(
            days=1
        )
    )


    request = DataAccessRequest(
        actor_id="SYSTEM",

        parcel_id="PARCEL-001",

        permission=(
            DataPermission.PROCESS
        ),

        purpose=(
            DataPurpose
            .DIGITAL_TWIN_OPERATION
        ),

        data_category=(
            "MACHINE_EVIDENCE"
        ),
    )


    result = engine.evaluate(
        request=request,
        consents=[
            consent
        ],
    )


    assert result.allowed is False


def test_unknown_category_is_denied():

    consent = build_consent()


    request = DataAccessRequest(
        actor_id="SYSTEM",

        parcel_id="PARCEL-001",

        permission=(
            DataPermission.READ
        ),

        purpose=(
            DataPurpose
            .DIGITAL_TWIN_OPERATION
        ),

        data_category=(
            "PRIVATE_EXTERNAL_DATA"
        ),
    )


    result = engine.evaluate(
        request=request,
        consents=[
            consent
        ],
    )


    assert result.allowed is False