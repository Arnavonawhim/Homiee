import json
import hashlib
import secrets
import logging
from django.conf import settings
from authentication.otp_service import get_redis
from .sms import send_sms

logger = logging.getLogger("userdetails")

def _expiry_minutes():
    return getattr(settings, "SOS_OTP_EXPIRY_MINUTES", 10)

def _max_attempts():
    return getattr(settings, "SOS_OTP_MAX_ATTEMPTS", 5)

def _resend_cooldown_seconds():
    return getattr(settings, "SOS_OTP_RESEND_COOLDOWN_SECONDS", 60)

def _key(user_id):
    return f"me:sos_otp:{user_id}"

def _key_cooldown(user_id):
    return f"me:sos_otp_cooldown:{user_id}"

def _hash(value):
    return hashlib.sha256(value.encode()).hexdigest()

def _generate_code():
    return str(secrets.randbelow(900000) + 100000)

def _send(mobile, code):
    send_sms(
        mobile,
        f"Your HoMiee emergency contact verification code is {code}. "
        f"It expires in {_expiry_minutes()} minute(s).",
    )

def send_sos_otp(user_id, mobile, extra):
    r = get_redis()
    code = _generate_code()
    payload = json.dumps({
        "hash": _hash(code),
        "mobile": mobile,
        "attempts": 0,
        "extra": extra,
    })
    r.setex(_key(user_id), _expiry_minutes() * 60, payload)
    r.setex(_key_cooldown(user_id), _resend_cooldown_seconds(), "1")
    _send(mobile, code)
    logger.info("SOS OTP sent for user %s to %s", user_id, mobile)
    return code

def resend_sos_otp(user_id):
    r = get_redis()
    raw = r.get(_key(user_id))
    if not raw:
        return False, "No pending verification found. Please request an OTP first.", None
    cooldown_ttl = r.ttl(_key_cooldown(user_id))
    if cooldown_ttl > 0:
        return False, f"Please wait {cooldown_ttl} second(s) before requesting another OTP.", None
    payload = json.loads(raw)
    code = _generate_code()
    payload["hash"] = _hash(code)
    payload["attempts"] = 0
    r.setex(_key(user_id), _expiry_minutes() * 60, json.dumps(payload))
    r.setex(_key_cooldown(user_id), _resend_cooldown_seconds(), "1")
    _send(payload["mobile"], code)
    logger.info("SOS OTP resent for user %s", user_id)
    return True, "OTP resent to the emergency contact number.", code

def verify_sos_otp(user_id, code):
    r = get_redis()
    raw = r.get(_key(user_id))
    if not raw:
        return False, "OTP expired or not requested. Please request a new one.", None
    payload = json.loads(raw)
    if payload["hash"] == _hash(code):
        r.delete(_key(user_id))
        r.delete(_key_cooldown(user_id))
        logger.info("SOS OTP verified for user %s", user_id)
        return True, "Emergency contact verified successfully.", payload
    payload["attempts"] += 1
    attempts_remaining = _max_attempts() - payload["attempts"]
    if payload["attempts"] >= _max_attempts():
        r.delete(_key(user_id))
        r.delete(_key_cooldown(user_id))
        logger.warning("SOS OTP attempts exhausted for user %s", user_id)
        return False, "Too many failed attempts. Please request a new OTP.", None
    ttl = r.ttl(_key(user_id))
    if ttl > 0:
        r.setex(_key(user_id), ttl, json.dumps(payload))
    return False, f"Invalid OTP. {attempts_remaining} attempt(s) remaining.", None
