from services.password_service import (
    PasswordService,
)

from services.token_service import (
    TokenService,
)


def test_password_hash_and_verify():

    service = PasswordService()

    password = (
        "AgriculturalTwin123!"
    )

    hashed = (
        service.hash_password(
            password
        )
    )


    assert hashed != password

    assert service.verify_password(
        password,
        hashed,
    ) is True

    assert service.verify_password(
        "wrong-password",
        hashed,
    ) is False


def test_access_token_roundtrip():

    service = TokenService()


    token = (
        service.create_access_token(
            user_id="USER-001",
            email="farmer@example.com",
            system_role="USER",
        )
    )


    payload = (
        service.decode_access_token(
            token
        )
    )


    assert (
        payload["sub"]
        == "USER-001"
    )

    assert (
        payload["email"]
        == "farmer@example.com"
    )

    assert (
        payload["system_role"]
        == "USER"
    )

    assert (
        payload["type"]
        == "access"
    )