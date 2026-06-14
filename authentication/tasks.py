import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from authentication import sms_service

logger = logging.getLogger("authentication")

def _send_html_email(to_email: str, subject: str, template_name: str, context: dict) -> bool:
    try:
        html_body = render_to_string(f"emails/{template_name}", context)
        plain_body = render_to_string(f"emails/{template_name.replace('.html', '_plain.txt')}", context)
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
        logger.info("Email sent successfully to %s (template=%s)", to_email, template_name)
        return True
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to_email, str(exc))
        raise exc

def send_otp_email(email: str, otp: str, purpose: str):
    logger.info("Sending OTP email to %s (purpose=%s)", email, purpose)
    if purpose == "registration":
        subject = "Verify your MaidEasy account"
        template = "otp_verification.html"
    else:
        subject = "MaidEasy password reset"
        template = "otp_password_reset.html"
    context = {
        "otp": otp,
        "expiry_minutes": settings.OTP_EXPIRY_MINUTES,
        "support_email": "support@maideasy.com",
    }
    _send_html_email(email, subject, template, context)

def send_otp_sms(mobile: str, otp: str, purpose: str):
    logger.info("Sending OTP SMS to %s (purpose=%s)", mobile, purpose)
    sms_service.send_otp_sms(mobile, otp, purpose)

def send_welcome_email(email: str, username: str):
    logger.info("Sending welcome email to %s", email)
    context = {
        "username": username,
        "support_email": "support@maideasy.com",
        "app_url": "https://maideasy.com",
    }
    _send_html_email(email, "Welcome to MaidEasy", "welcome.html", context)

def send_goodbye_email(email: str, username: str):
    logger.info("Sending goodbye email to %s", email)
    context = {
        "username": username,
        "support_email": "support@maideasy.com",
        "app_url": "https://maideasy.com",
    }
    _send_html_email(email, "Goodbye from MaidEasy", "goodbye.html", context)