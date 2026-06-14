import logging
from django.conf import settings

logger = logging.getLogger("authentication")

def send_otp_sms(mobile: str, otp_code: str, purpose: str) -> bool:
    backend = getattr(settings, "SMS_BACKEND", "console")
    if backend == "console":
        logger.info("SMS OTP [%s] to %s (purpose=%s)", otp_code, mobile, purpose)
        return True
    raise NotImplementedError(f"SMS backend '{backend}' is not implemented yet.")
