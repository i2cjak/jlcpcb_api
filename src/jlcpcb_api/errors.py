from __future__ import annotations


class JLCError(Exception):
    """Base exception for the reverse-engineered JLCPCB client."""


class JLCTransportError(JLCError):
    """Raised for request transport failures."""


class JLCProtocolError(JLCError):
    """Raised when the server response cannot be interpreted."""


class JLCBusinessError(JLCError):
    """Raised when the API returns a non-success business code."""

    def __init__(
        self,
        *,
        code: int,
        message: str,
        request_id: str | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.request_id = request_id
        self.status_code = status_code
