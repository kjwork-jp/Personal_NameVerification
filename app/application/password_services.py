"""Password hashing helpers for local user authentication."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from dataclasses import dataclass

from app.domain.errors import ValidationError

PASSWORD_ALGORITHM = "pbkdf2_sha256"
PASSWORD_HASH_NAME = "sha256"
DEFAULT_PASSWORD_ITERATIONS = 310_000
MIN_PASSWORD_ITERATIONS = 310_000
MIN_SALT_BYTES = 16


@dataclass(frozen=True, slots=True)
class PasswordHash:
    """Stored password hash fields for the users table."""

    algorithm: str
    iterations: int
    salt: str
    password_hash: str


def hash_password(
    password: str,
    *,
    iterations: int = DEFAULT_PASSWORD_ITERATIONS,
    salt_bytes: bytes | None = None,
) -> PasswordHash:
    """Hash a plain password with PBKDF2-SHA256 and a per-user salt."""

    if password == "":
        raise ValidationError("password is required")
    if iterations < MIN_PASSWORD_ITERATIONS:
        raise ValidationError("password iterations is below the minimum")

    actual_salt = salt_bytes if salt_bytes is not None else secrets.token_bytes(MIN_SALT_BYTES)
    if len(actual_salt) < MIN_SALT_BYTES:
        raise ValidationError("password salt is too short")

    digest = _pbkdf2_digest(password=password, salt=actual_salt, iterations=iterations)
    return PasswordHash(
        algorithm=PASSWORD_ALGORITHM,
        iterations=iterations,
        salt=_base64_encode(actual_salt),
        password_hash=_base64_encode(digest),
    )


def verify_password(password: str, stored: PasswordHash) -> bool:
    """Return True when the plain password matches the stored PBKDF2 hash."""

    if password == "" or stored.algorithm != PASSWORD_ALGORITHM or stored.iterations <= 0:
        return False

    try:
        salt = _base64_decode(stored.salt)
        expected_hash = _base64_decode(stored.password_hash)
    except ValueError:
        return False

    actual_hash = _pbkdf2_digest(
        password=password,
        salt=salt,
        iterations=stored.iterations,
    )
    return hmac.compare_digest(actual_hash, expected_hash)


def needs_rehash(
    stored: PasswordHash,
    *,
    desired_iterations: int = DEFAULT_PASSWORD_ITERATIONS,
) -> bool:
    """Return True when the stored hash should be upgraded."""

    if desired_iterations < MIN_PASSWORD_ITERATIONS:
        raise ValidationError("desired password iterations is below the minimum")
    return stored.algorithm != PASSWORD_ALGORITHM or stored.iterations < desired_iterations


def _pbkdf2_digest(*, password: str, salt: bytes, iterations: int) -> bytes:
    return hashlib.pbkdf2_hmac(
        PASSWORD_HASH_NAME,
        password.encode("utf-8"),
        salt,
        iterations,
    )


def _base64_encode(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _base64_decode(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"), validate=True)
