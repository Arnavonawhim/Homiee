import logging
import requests
from django.conf import settings
from twilio.rest import Client

logger = logging.getLogger("userdetails")

def send_sms(mobile, message):
    backend = getattr(settings, "SMS_BACKEND", "console")
    if backend == "fast2sms":
        return _send_fast2sms(mobile, message)
    if backend == "twilio":
        return _send_twilio(mobile, message)
    logger.info("[console-sms] to=%s message=%s", mobile, message)
    return True

def _send_fast2sms(mobile, message):
    url = "https://www.fast2sms.com/dev/bulkV2"
    headers = {"authorization": settings.FAST2SMS_API_KEY}
    payload = {
        "route": "q",
        "message": message,
        "language": "english",
        "numbers": _normalize_for_gateway(mobile),
    }
    resp = requests.post(url, data=payload, headers=headers, timeout=10)
    ok = resp.status_code == 200 and resp.json().get("return") is True
    if not ok:
        logger.error("Fast2SMS failed for %s: %s", mobile, resp.text)
    return ok

def _send_twilio(mobile, message):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    number = mobile if mobile.startswith("+") else "+91" + _normalize_for_gateway(mobile)
    client.messages.create(body=message, from_=settings.TWILIO_FROM_NUMBER, to=number)
    return True

def _normalize_for_gateway(mobile):
    digits = "".join(ch for ch in (mobile or "") if ch.isdigit())
    return digits[-10:] if len(digits) >= 10 else digits
