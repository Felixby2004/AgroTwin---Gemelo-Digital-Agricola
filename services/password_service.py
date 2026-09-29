from pwdlib import (
    PasswordHash,
)


class PasswordService:

    def __init__(
        self,
    ):

        self.password_hash = (
            PasswordHash.recommended()
        )


    def hash_password(
        self,
        password: str,
    ) -> str:

        if len(password) < 8:

            raise ValueError(
                "Password must contain "
                "at least 8 characters."
            )


        return (
            self.password_hash.hash(
                password
            )
        )


    def verify_password(
        self,
        plain_password: str,
        password_hash: str,
    ) -> bool:

        try:

            return (
                self.password_hash
                .verify(
                    plain_password,
                    password_hash,
                )
            )

        except Exception:

            return False