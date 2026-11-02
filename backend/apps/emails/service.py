"""
Swarna Khata Book — Email Service Orchestrator
Coordinates email generation, token URL resolution, and secure provider dispatch.
Ensures email delivery failures cannot corrupt user authentication state.
"""

import logging
from typing import Optional, Dict, Any
from decouple import config
from apps.emails.provider import get_email_provider, EmailDeliveryError
from apps.emails.templates import get_password_reset_email

logger = logging.getLogger('swarnakhata.emails')
audit_logger = logging.getLogger('swarnakhata.audit')


class EmailService:
    """
    High-level transactional email service facade.
    """

    @classmethod
    def get_frontend_url(cls) -> str:
        """
        Resolve the canonical frontend base URL for verification / reset links.
        """
        url = config('FRONTEND_URL', default='').strip() or config('APP_URL', default='').strip()
        if not url:
            # Fallback to standard local Vite dev port or production Vercel
            url = 'http://localhost:5173'
        return url.rstrip('/')

    @classmethod
    def send_password_reset_email(
        cls,
        user_id: int,
        username: str,
        email: str,
        tenant_schema: str,
        raw_token: str,
        shop_name: str = "Swarna Khata Book",
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrates password reset email delivery.
        Never leaks raw tokens to logs.
        Isolates failures so authentication state remains untouched.
        """
        frontend_url = cls.get_frontend_url()
        reset_url = f"{frontend_url}/reset-password?token={raw_token}"

        subject, html_body, text_body = get_password_reset_email(
            username=username,
            reset_url=reset_url,
            shop_name=shop_name,
            expiry_minutes=15
        )

        provider = get_email_provider()
        masked_email = f"{email[:3]}***@{email.split('@')[-1]}" if '@' in email else "***"

        audit_logger.info(
            "PASSWORD_RESET_DISPATCH_TRIGGERED: user_id=%d schema='%s' email='%s' ip='%s'",
            user_id, tenant_schema, masked_email, ip_address or '-'
        )

        try:
            result = provider.send_email(
                to_email=email,
                to_name=username,
                subject=subject,
                html_content=html_body,
                text_content=text_body
            )
            audit_logger.info(
                "PASSWORD_RESET_EMAIL_SENT: user_id=%d schema='%s' message_id='%s'",
                user_id, tenant_schema, result.get("message_id", "ok")
            )
            return {"status": "success", "result": result}
        except EmailDeliveryError as exc:
            logger.error(
                "PASSWORD_RESET_EMAIL_DELIVERY_FAILED: user_id=%d schema='%s' error='%s'",
                user_id, tenant_schema, exc
            )
            # Do NOT re-raise to protect user and prevent enumeration leaks
            return {"status": "failed", "error": str(exc)}
        except Exception as exc:
            logger.exception(
                "PASSWORD_RESET_EMAIL_UNEXPECTED_ERROR: user_id=%d schema='%s'",
                user_id, tenant_schema
            )
            return {"status": "failed", "error": "Internal delivery error"}
