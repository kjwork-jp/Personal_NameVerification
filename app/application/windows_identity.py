"""Windows identity resolution helpers for OS-auth login."""

from __future__ import annotations

import getpass
import os
import platform
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WindowsIdentity:
    """Current OS user identity used by Windows authentication."""

    account_name: str
    display_name: str
    sid: str | None = None


class WindowsIdentityError(RuntimeError):
    """Raised when the current OS identity cannot be resolved."""


def current_windows_identity() -> WindowsIdentity:
    """Return the current Windows logon identity.

    The application treats the active OS session as already authenticated. SID lookup is
    best-effort so tests and non-Windows development environments can still exercise the
    flow by using the account name.
    """

    if platform.system().lower() != "windows":
        raise WindowsIdentityError("Windows authentication is available only on Windows")

    username = getpass.getuser().strip()
    if not username:
        raise WindowsIdentityError("current Windows user name is empty")
    domain = os.environ.get("USERDOMAIN", "").strip()
    account_name = f"{domain}\\{username}" if domain else username
    sid = _lookup_windows_sid(account_name)
    return WindowsIdentity(
        account_name=account_name,
        display_name=username,
        sid=sid,
    )


def _lookup_windows_sid(account_name: str) -> str | None:
    try:
        import win32security  # type: ignore[import-not-found]

        sid, _domain, _account_type = win32security.LookupAccountName(None, account_name)
        return win32security.ConvertSidToStringSid(sid)
    except Exception:
        return None
