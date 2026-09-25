"""WinForge exception hierarchy."""

from __future__ import annotations

from typing import Optional


class WinForgeError(Exception):
    """Base exception for all WinForge errors."""

    def __init__(
        self,
        message: str,
        *,
        details: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details
        self.suggestion = suggestion

    def user_message(self) -> str:
        """Format a user-friendly error message."""
        parts = [self.message]
        if self.details:
            parts.append(f"\nReason:\n{self.details}")
        if self.suggestion:
            parts.append(f"\nPossible solution:\n{self.suggestion}")
        return "\n".join(parts)


class ToyError(WinForgeError):
    """Error originating from a specific Toy."""

    def __init__(
        self,
        toy_name: str,
        message: str,
        *,
        details: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        super().__init__(message, details=details, suggestion=suggestion)
        self.toy_name = toy_name

    def user_message(self) -> str:
        header = f"Toy: {self.toy_name}\n\n{self.message}"
        parts = [header]
        if self.details:
            parts.append(f"\nReason:\n{self.details}")
        if self.suggestion:
            parts.append(f"\nPossible solution:\n{self.suggestion}")
        return "\n".join(parts)


class PermissionError(WinForgeError):
    """Raised when administrator privileges are required but missing."""

    def __init__(
        self,
        message: str = "Administrator privileges are required for this operation.",
        *,
        details: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        if suggestion is None:
            suggestion = (
                "Close WinForge and restart it by right-clicking the shortcut "
                "and selecting 'Run as administrator'."
            )
        super().__init__(message, details=details, suggestion=suggestion)


class UnsupportedVersionError(WinForgeError):
    """Raised when the current Windows version does not support a feature."""

    def __init__(
        self,
        required: str,
        current: str,
        *,
        details: Optional[str] = None,
    ) -> None:
        message = f"This feature requires {required}."
        if details is None:
            details = f"Detected Windows version: {current}"
        suggestion = (
            "This Toy is not available on your system. "
            "Consider upgrading Windows or choosing a different Toy."
        )
        super().__init__(message, details=details, suggestion=suggestion)
        self.required = required
        self.current = current


class ConfigurationError(WinForgeError):
    """Raised for configuration load/save problems."""

    pass


class BackupError(WinForgeError):
    """Raised when backup or restore operations fail."""

    pass
