"""
Swarna Khata Book — Transactional Email Templates
Branded HTML and plain-text templates for password reset and notifications.
"""

from typing import Tuple


def get_password_reset_email(
    username: str,
    reset_url: str,
    shop_name: str = "Swarna Khata Book",
    expiry_minutes: int = 15
) -> Tuple[str, str, str]:
    """
    Generate subject, HTML body, and plaintext body for password reset.
    Branded with Swarna Khata luxury gold & slate styling.
    """
    subject = f"Reset your password for {shop_name}"

    text_content = f"""Hello {username},

We received a request to reset your password for your account on {shop_name}.

To choose a new password, click the link below (valid for {expiry_minutes} minutes):
{reset_url}

Security Notice:
- This link is single-use and will expire in {expiry_minutes} minutes.
- If you did not make this request, you can safely ignore this email. Your password will remain unchanged.
- Never share this link or your credentials with anyone.

Best regards,
The {shop_name} Security Team
"""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reset Your Password</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      margin: 0;
      padding: 0;
      background-color: #F8FAFC;
      color: #1E293B;
    }}
    .email-container {{
      max-width: 580px;
      margin: 40px auto;
      background-color: #FFFFFF;
      border-radius: 16px;
      overflow: hidden;
      border: 1px solid #E2E8F0;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
    }}
    .header {{
      background: linear-gradient(135deg, #B45309 0%, #D97706 50%, #F59E0B 100%);
      padding: 32px 24px;
      text-align: center;
      color: #FFFFFF;
    }}
    .header h1 {{
      margin: 0;
      font-size: 24px;
      font-weight: 800;
      letter-spacing: -0.5px;
    }}
    .header p {{
      margin: 6px 0 0;
      font-size: 13px;
      opacity: 0.9;
      font-weight: 500;
    }}
    .content {{
      padding: 36px 32px;
    }}
    .greeting {{
      font-size: 17px;
      font-weight: 600;
      margin-bottom: 16px;
      color: #0F172A;
    }}
    .message {{
      font-size: 14px;
      line-height: 1.6;
      color: #475569;
      margin-bottom: 28px;
    }}
    .cta-container {{
      text-align: center;
      margin: 32px 0;
    }}
    .cta-button {{
      display: inline-block;
      background: linear-gradient(135deg, #D97706 0%, #B45309 100%);
      color: #FFFFFF !important;
      text-decoration: none;
      font-size: 15px;
      font-weight: 700;
      padding: 14px 36px;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(217, 119, 6, 0.3);
    }}
    .expiry-banner {{
      background-color: #FEF3C7;
      border: 1px solid #FDE68A;
      border-radius: 10px;
      padding: 12px 16px;
      font-size: 13px;
      color: #92400E;
      margin-bottom: 24px;
    }}
    .alt-link {{
      font-size: 12px;
      color: #64748B;
      word-break: break-all;
      margin-top: 24px;
      line-height: 1.5;
    }}
    .alt-link a {{
      color: #D97706;
      text-decoration: underline;
    }}
    .footer {{
      background-color: #F8FAFC;
      border-top: 1px solid #E2E8F0;
      padding: 24px;
      text-align: center;
      font-size: 12px;
      color: #94A3B8;
      line-height: 1.5;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <h1>✨ {shop_name}</h1>
      <p>Jewellery ERP & Khata Management</p>
    </div>
    <div class="content">
      <div class="greeting">Hello {username},</div>
      <div class="message">
        We received a request to reset your password for your account on <strong>{shop_name}</strong>.
        Please click the button below to choose a secure new password meeting our Jewellery Shield standards.
      </div>
      <div class="expiry-banner">
        ⏱ <strong>Time Sensitive:</strong> This password reset link is valid for <strong>{expiry_minutes} minutes</strong> and can only be used once.
      </div>
      <div class="cta-container">
        <a href="{reset_url}" target="_blank" class="cta-button">Reset My Password</a>
      </div>
      <div class="alt-link">
        If the button above does not work, copy and paste this link into your browser:<br>
        <a href="{reset_url}">{reset_url}</a>
      </div>
    </div>
    <div class="footer">
      <p>If you did not request this password reset, you can safely ignore this email.<br>
      Your account credentials remain secure and unchanged.<br><br>
      © 2026 {shop_name} • Cloud Jewellery ERP</p>
    </div>
  </div>
</body>
</html>"""

    return subject, html_content, text_content
