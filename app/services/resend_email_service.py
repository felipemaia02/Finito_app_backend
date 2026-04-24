"""Resend email service implementation using the Resend API."""

import resend

from app.domain.interfaces.email_service_interface import IEmailService
from app.infrastructure.settings import get_settings
from app.infrastructure.logger import get_logger

logger = get_logger(__name__)


class ResendEmailService(IEmailService):
    """Sends transactional emails via the Resend API."""

    def __init__(self):
        self.settings = get_settings()
        resend.api_key = self.settings.resend_api_key

    async def send_verification_email(self, to_email: str, code: str) -> None:
        """
        Deliver a 6-digit verification code to the user's inbox.

        Args:
            to_email: Recipient email address
            code: Plain-text verification code (never stored as-is)

        Raises:
            Exception: If the Resend API call fails
        """
        try:
            logger.info(f"Sending verification email to {to_email[:3]}***")
            params: resend.Emails.SendParams = {
                "from": self.settings.resend_from_email,
                "to": [to_email],
                "subject": "Finito — Verifique seu endereço de e-mail",
                "html": _build_email_html(code),
            }
            resend.Emails.send(params)
            logger.info(f"Verification email sent to {to_email[:3]}***")
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
            raise


def _build_email_html(code: str) -> str:
    return f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto;padding:32px">
      <h2 style="color:#1a1a1a">Verifique seu e-mail</h2>
      <p style="color:#555">Use o código abaixo para confirmar seu cadastro no <strong>Finito</strong>.</p>
      <div style="font-size:36px;font-weight:bold;letter-spacing:8px;
                  background:#f4f4f4;padding:16px 24px;border-radius:8px;
                  text-align:center;margin:24px 0">
        {code}
      </div>
      <p style="color:#888;font-size:13px">
        Este código expira em <strong>15 minutos</strong>.<br>
        Se você não solicitou este cadastro, ignore este e-mail.
      </p>
    </div>
    """
