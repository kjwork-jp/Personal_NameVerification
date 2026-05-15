from __future__ import annotations

import pytest

from app.application.password_services import (
    DEFAULT_PASSWORD_ITERATIONS,
    MIN_PASSWORD_ITERATIONS,
    MIN_SALT_BYTES,
    PASSWORD_ALGORITHM,
    PasswordHash,
    hash_password,
    needs_rehash,
    verify_password,
)
from app.domain.errors import ValidationError


def test_hash_password_generates_pbkdf2_fields() -> None:
    stored = hash_password("correct horse battery staple")

    assert stored.algorithm == PASSWORD_ALGORITHM
    assert stored.iterations == DEFAULT_PASSWORD_ITERATIONS
    assert stored.salt
    assert stored.password_hash
    assert stored.salt != stored.password_hash


def test_hash_password_uses_random_salt() -> None:
    first = hash_password("same-password")
    second = hash_password("same-password")

    assert first.salt != second.salt
    assert first.password_hash != second.password_hash


def test_verify_password_accepts_matching_password() -> None:
    stored = hash_password(
        "secret-password",
        salt_bytes=b"0123456789abcdef",
    )

    assert verify_password("secret-password", stored) is True


def test_verify_password_rejects_wrong_password() -> None:
    stored = hash_password(
        "secret-password",
        salt_bytes=b"0123456789abcdef",
    )

    assert verify_password("wrong-password", stored) is False


def test_verify_password_rejects_invalid_stored_hash() -> None:
    stored = PasswordHash(
        algorithm=PASSWORD_ALGORITHM,
        iterations=DEFAULT_PASSWORD_ITERATIONS,
        salt="not-base64",
        password_hash="not-base64",
    )

    assert verify_password("secret-password", stored) is False


def test_verify_password_rejects_unsupported_algorithm() -> None:
    stored = hash_password("secret-password")
    unsupported = PasswordHash(
        algorithm="plain",
        iterations=stored.iterations,
        salt=stored.salt,
        password_hash=stored.password_hash,
    )

    assert verify_password("secret-password", unsupported) is False


def test_hash_password_rejects_empty_password() -> None:
    with pytest.raises(ValidationError, match="password is required"):
        hash_password("")


def test_hash_password_rejects_low_iterations() -> None:
    with pytest.raises(ValidationError, match="iterations"):
        hash_password("secret-password", iterations=MIN_PASSWORD_ITERATIONS - 1)


def test_hash_password_rejects_short_salt() -> None:
    with pytest.raises(ValidationError, match="salt"):
        hash_password("secret-password", salt_bytes=b"short")


def test_needs_rehash_detects_low_iteration_count() -> None:
    stored = PasswordHash(
        algorithm=PASSWORD_ALGORITHM,
        iterations=MIN_PASSWORD_ITERATIONS - 1,
        salt="AA==",
        password_hash="AA==",
    )

    assert needs_rehash(stored) is True


def test_needs_rehash_detects_algorithm_change() -> None:
    stored = PasswordHash(
        algorithm="legacy",
        iterations=DEFAULT_PASSWORD_ITERATIONS,
        salt="AA==",
        password_hash="AA==",
    )

    assert needs_rehash(stored) is True


def test_needs_rehash_accepts_current_hash() -> None:
    stored = hash_password(
        "secret-password",
        salt_bytes=b"x" * MIN_SALT_BYTES,
    )

    assert needs_rehash(stored) is False
