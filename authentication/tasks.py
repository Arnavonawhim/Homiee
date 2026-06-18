import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from authentication import sms_service

logger = logging.getLogger("authentication")


_BASE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{subject}</title>
</head>
<body style="margin:0;padding:0;background:#f4f4f7;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f7;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0"
               style="background:#ffffff;border-radius:8px;overflow:hidden;
                      box-shadow:0 2px 8px rgba(0,0,0,0.08);max-width:600px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:#4F46E5;padding:32px 40px;text-align:center;">
              <h1 style="margin:0;color:#ffffff;font-size:24px;font-weight:700;
                         letter-spacing:0.5px;">MaidEasy</h1>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px 40px 32px;">
              {body}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f9f9fb;padding:24px 40px;
                       border-top:1px solid #e8e8ed;text-align:center;">
              <p style="margin:0;font-size:12px;color:#9ca3af;">
                Need help? Contact us at
                <a href="mailto:{support_email}" style="color:#4F46E5;text-decoration:none;">
                  {support_email}
                </a>
              </p>
              <p style="margin:8px 0 0;font-size:12px;color:#9ca3af;">
                &copy; 2025 MaidEasy. All rights reserved.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def _build_email(subject: str, body_html: str, support_email: str) -> str:
    return _BASE_HTML.format(
        subject=subject,
        body=body_html,
        support_email=support_email,
    )


def _send_email(to_email: str, subject: str, plain_body: str, html_body: str) -> bool:
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
        logger.info("Email sent to %s | subject=%s", to_email, subject)
        return True
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to_email, str(exc))
        raise


def send_otp_email(email: str, otp: str, purpose: str):
    logger.info("Sending OTP email to %s (purpose=%s)", email, purpose)

    support = "support@maideasy.com"

    if purpose == "registration":
        subject = "Verify your MaidEasy account"
        heading = "Verify Your Account"
        intro = "Thanks for signing up! Use the OTP below to complete your registration."
        note = "This code is valid for"
    else:
        subject = "MaidEasy — Password Reset OTP"
        heading = "Reset Your Password"
        intro = "We received a request to reset your password. Use the OTP below to proceed."
        note = "This code is valid for"

    body_html = f"""
      <h2 style="margin:0 0 16px;font-size:20px;color:#111827;">{heading}</h2>
      <p style="margin:0 0 24px;font-size:15px;color:#374151;line-height:1.6;">
        {intro}
      </p>

      <!-- OTP Box -->
      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
        <tr>
          <td align="center">
            <div style="display:inline-block;background:#f3f4f6;border:1px dashed #d1d5db;
                        border-radius:8px;padding:20px 48px;">
              <span style="font-size:36px;font-weight:700;letter-spacing:8px;
                           color:#4F46E5;font-family:monospace;">{otp}</span>
            </div>
          </td>
        </tr>
      </table>

      <p style="margin:0 0 8px;font-size:13px;color:#6b7280;text-align:center;">
        {note} <strong>{settings.OTP_EXPIRY_MINUTES} minutes</strong>.
        Do not share this code with anyone.
      </p>
      <p style="margin:24px 0 0;font-size:13px;color:#9ca3af;text-align:center;">
        If you didn't request this, you can safely ignore this email.
      </p>
    """

    plain_body = (
        f"{heading}\n\n"
        f"{intro}\n\n"
        f"Your OTP: {otp}\n\n"
        f"This code expires in {settings.OTP_EXPIRY_MINUTES} minutes. "
        f"Do not share it with anyone.\n\n"
        f"If you didn't request this, ignore this email.\n\n"
        f"— MaidEasy Support ({support})"
    )

    html_body = _build_email(subject, body_html, support)
    _send_email(email, subject, plain_body, html_body)



def send_welcome_email(email: str, username: str):
    logger.info("Sending welcome email to %s", email)

    support = "support@maideasy.com"
    subject = "Welcome to MaidEasy! "

    body_html = f"""
      <h2 style="margin:0 0 16px;font-size:20px;color:#111827;">
        Welcome aboard, {username}!
      </h2>
      <p style="margin:0 0 16px;font-size:15px;color:#374151;line-height:1.6;">
        Your MaidEasy account is all set. We're excited to have you with us.
      </p>
      <p style="margin:0 0 24px;font-size:15px;color:#374151;line-height:1.6;">
        You can now log in and start exploring our services.
      </p>
      <table cellpadding="0" cellspacing="0" style="margin:0 auto 24px;">
        <tr>
          <td align="center" bgcolor="#4F46E5" style="border-radius:6px;">
            <a href="https://maideasy.com"
               style="display:inline-block;padding:12px 32px;font-size:15px;
                      font-weight:600;color:#ffffff;text-decoration:none;
                      border-radius:6px;">
              Go to MaidEasy
            </a>
          </td>
        </tr>
      </table>
      <p style="margin:0;font-size:13px;color:#9ca3af;text-align:center;">
        If you have any questions, we're always here to help.
      </p>
    """

    plain_body = (
        f"Welcome to MaidEasy, {username}!\n\n"
        f"Your account is ready. Log in at https://maideasy.com\n\n"
        f"If you need help, reach us at {support}.\n\n"
        f"— The MaidEasy Team"
    )

    html_body = _build_email(subject, body_html, support)
    _send_email(email, subject, plain_body, html_body)



def send_goodbye_email(email: str, username: str):
    logger.info("Sending goodbye email to %s", email)

    support = "support@maideasy.com"
    subject = "Your MaidEasy account has been deleted"

    body_html = f"""
      <h2 style="margin:0 0 16px;font-size:20px;color:#111827;">
        Goodbye, {username}
      </h2>
      <p style="margin:0 0 16px;font-size:15px;color:#374151;line-height:1.6;">
        Your MaidEasy account has been permanently deleted as requested.
        All your data has been removed from our systems.
      </p>
      <p style="margin:0 0 24px;font-size:15px;color:#374151;line-height:1.6;">
        We're sorry to see you go. If this was a mistake or you'd like to come back
        in the future, you're always welcome to create a new account.
      </p>
      <p style="margin:0;font-size:13px;color:#9ca3af;text-align:center;">
        If you didn't request this deletion, please contact us immediately.
      </p>
    """

    plain_body = (
        f"Goodbye, {username}.\n\n"
        f"Your MaidEasy account has been permanently deleted. "
        f"All your data has been removed.\n\n"
        f"If this was a mistake, contact us at {support}.\n\n"
        f"— The MaidEasy Team"
    )

    html_body = _build_email(subject, body_html, support)
    _send_email(email, subject, plain_body, html_body)



def send_otp_sms(mobile: str, otp: str, purpose: str):
    logger.info("Sending OTP SMS to %s (purpose=%s)", mobile, purpose)
    sms_service.send_otp_sms(mobile, otp, purpose)