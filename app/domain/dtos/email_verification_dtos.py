"""
DTOs for email verification use cases.
"""

from typing import NamedTuple


class SendVerificationEmailInput(NamedTuple):
    user_id: str
    email: str


class VerifyEmailCodeInput(NamedTuple):
    user_id: str
    code: str


class ResendVerificationEmailInput(NamedTuple):
    user_id: str


class RequestVerificationInput(NamedTuple):
    email: str
