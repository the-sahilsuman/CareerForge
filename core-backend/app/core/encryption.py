from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


class TokenEncryptionError(Exception):
    """Raised when OAuth token encryption/decryption fails."""


def _get_fernet() -> Fernet:
    try:
        return Fernet(
            settings.email_token_encryption_key.encode()
        )
    except Exception as exc:
        raise TokenEncryptionError(
            "Invalid email token encryption key."
        ) from exc


def encrypt_token(token: str) -> str:
    try:
        return _get_fernet().encrypt(
            token.encode("utf-8")
        ).decode("utf-8")
    except Exception as exc:
        raise TokenEncryptionError(
            "Unable to encrypt OAuth token."
        ) from exc


def decrypt_token(encrypted_token: str) -> str:
    try:
        return _get_fernet().decrypt(
            encrypted_token.encode("utf-8")
        ).decode("utf-8")
    except InvalidToken as exc:
        raise TokenEncryptionError(
            "Unable to decrypt OAuth token."
        ) from exc