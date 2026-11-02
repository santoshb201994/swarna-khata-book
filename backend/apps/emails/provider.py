"""
Swarna Khata Book — Email Provider Abstraction
Implements reusable Brevo Transactional Email provider via REST API using HTTPX.
Follows least-privilege, structured logging, and non-blocking asynchronous design.
"""

import abc
import logging
from typing import Dict, Any, Optional, List
import httpx
from decouple import config

logger = logging.getLogger('swarnakhata.emails')

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


class EmailDeliveryError(Exception):
    """Raised when email delivery fails via the configured provider."""
    pass


class BaseEmailProvider(abc.ABC):
    """
    Abstract email provider interface allowing clean pluggability of providers
    (Brevo, SendGrid, Amazon SES, or Console/Mock for local tests).
    """

    @abc.abstractmethod
    async def send_email_async(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Asynchronously dispatch transactional email."""
        pass

    @abc.abstractmethod
    def send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synchronously dispatch transactional email."""
        pass


class BrevoEmailProvider(BaseEmailProvider):
    """
    Production Brevo (Sendinblue) Transactional Email Provider.
    Communicates with Brevo REST API v3 using HTTPX with rigorous timeout
    and error handling.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        sender_email: Optional[str] = None,
        sender_name: Optional[str] = None,
        timeout: float = 10.0
    ):
        self.api_key = api_key or config('BREVO_API_KEY', default='').strip()
        self.sender_email = sender_email or config('BREVO_SENDER_EMAIL', default='noreply@swarnakhata.com').strip()
        self.sender_name = sender_name or config('BREVO_SENDER_NAME', default='Swarna Khata Book').strip()
        self.timeout = timeout

        if not self.api_key:
            logger.warning("BREVO_API_KEY is not configured in environment variables.")

    def _build_payload(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "sender": {
                "name": self.sender_name,
                "email": self.sender_email
            },
            "to": [
                {
                    "email": to_email.strip(),
                    "name": to_name.strip() or to_email.strip()
                }
            ],
            "subject": subject,
            "htmlContent": html_content
        }
        if text_content:
            payload["textContent"] = text_content
        return payload

    def _get_headers(self) -> Dict[str, str]:
        return {
            "accept": "application/json",
            "api-key": self.api_key,
            "content-type": "application/json"
        }

    async def send_email_async(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise EmailDeliveryError("Cannot send email: BREVO_API_KEY is not configured.")

        payload = self._build_payload(to_email, to_name, subject, html_content, text_content)
        headers = self._get_headers()

        masked_recipient = f"{to_email[:3]}***@{to_email.split('@')[-1]}" if '@' in to_email else "***"
        logger.info("BREVO_DISPATCH_ATTEMPT: recipient='%s' subject='%s'", masked_recipient, subject)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(BREVO_API_URL, headers=headers, json=payload)

            if response.status_code in (200, 201, 202):
                data = response.json()
                message_id = data.get("messageId", "ok")
                logger.info("BREVO_DISPATCH_SUCCESS: recipient='%s' messageId='%s'", masked_recipient, message_id)
                return {"status": "success", "message_id": message_id}
            else:
                err_text = response.text[:200]
                logger.error("BREVO_DISPATCH_FAILED: status=%d response='%s'", response.status_code, err_text)
                raise EmailDeliveryError(f"Brevo API error: HTTP {response.status_code}")

        except httpx.TimeoutException as exc:
            logger.error("BREVO_TIMEOUT: Request timed out after %.1fs", self.timeout)
            raise EmailDeliveryError("Brevo email dispatch timed out.") from exc
        except httpx.RequestError as exc:
            logger.error("BREVO_NETWORK_ERROR: %s", exc)
            raise EmailDeliveryError("Network error communicating with Brevo.") from exc

    def send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise EmailDeliveryError("Cannot send email: BREVO_API_KEY is not configured.")

        payload = self._build_payload(to_email, to_name, subject, html_content, text_content)
        headers = self._get_headers()

        masked_recipient = f"{to_email[:3]}***@{to_email.split('@')[-1]}" if '@' in to_email else "***"
        logger.info("BREVO_DISPATCH_ATTEMPT_SYNC: recipient='%s' subject='%s'", masked_recipient, subject)

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(BREVO_API_URL, headers=headers, json=payload)

            if response.status_code in (200, 201, 202):
                data = response.json()
                message_id = data.get("messageId", "ok")
                logger.info("BREVO_DISPATCH_SUCCESS: recipient='%s' messageId='%s'", masked_recipient, message_id)
                return {"status": "success", "message_id": message_id}
            else:
                err_text = response.text[:200]
                logger.error("BREVO_DISPATCH_FAILED: status=%d response='%s'", response.status_code, err_text)
                raise EmailDeliveryError(f"Brevo API error: HTTP {response.status_code}")

        except httpx.TimeoutException as exc:
            logger.error("BREVO_TIMEOUT: Request timed out after %.1fs", self.timeout)
            raise EmailDeliveryError("Brevo email dispatch timed out.") from exc
        except httpx.RequestError as exc:
            logger.error("BREVO_NETWORK_ERROR: %s", exc)
            raise EmailDeliveryError("Network error communicating with Brevo.") from exc


class ConsoleEmailProvider(BaseEmailProvider):
    """
    Development & Test Provider.
    Outputs email delivery details to logs instead of making live network requests.
    Prevents accidental outbound emails during local development.
    """

    async def send_email_async(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        return self.send_email(to_email, to_name, subject, html_content, text_content)

    def send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        logger.info(
            "CONSOLE_EMAIL_DISPATCH [DEV_MODE]: to='%s' name='%s' subject='%s'\nText:\n%s",
            to_email, to_name, subject, (text_content or '')[:300]
        )
        return {"status": "success", "message_id": "console-mock-id", "provider": "console"}


def get_email_provider() -> BaseEmailProvider:
    """
    Factory resolving active email provider.
    Returns BrevoEmailProvider if BREVO_API_KEY is configured, else ConsoleEmailProvider.
    """
    api_key = config('BREVO_API_KEY', default='').strip()
    if api_key:
        return BrevoEmailProvider(api_key=api_key)
    return ConsoleEmailProvider()
