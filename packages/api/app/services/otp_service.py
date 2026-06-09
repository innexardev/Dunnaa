"""OTP storage with Redis (production) and in-memory fallback (dev/tests)."""

import json
import random
import string
from datetime import UTC, datetime, timedelta

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

TTL_SECONDS = 300
MAX_VERIFY_ATTEMPTS = 5
_memory_store: dict[str, tuple[str, datetime]] = {}
_attempt_store: dict[str, int] = {}


def _redis_key(phone: str) -> str:
    return f"{settings.REDIS_PREFIX}otp:{phone}"


async def _get_redis():
    import redis.asyncio as aioredis

    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


async def store_code(phone: str, code: str | None = None) -> str:
    """Generate and store OTP. Returns the code."""
    otp = code or "".join(random.choices(string.digits, k=6))
    expires_at = datetime.now(UTC) + timedelta(seconds=TTL_SECONDS)
    payload = json.dumps({"code": otp, "expires_at": expires_at.isoformat()})

    try:
        redis = await _get_redis()
        await redis.setex(_redis_key(phone), TTL_SECONDS, payload)
        await redis.aclose()
        return otp
    except Exception as e:
        logger.warning("Redis OTP unavailable, using memory fallback", error=str(e))
        _memory_store[phone] = (otp, expires_at)
        return otp


async def verify_code(phone: str, code: str) -> bool:
    """Verify OTP and consume it on success."""
    attempts = await _get_attempts(phone)
    if attempts >= MAX_VERIFY_ATTEMPTS:
        logger.warning("OTP max attempts exceeded", phone=phone)
        return False

    stored = await _get_stored(phone)
    if not stored:
        return False

    otp, expires_at = stored
    if datetime.now(UTC) > expires_at:
        await delete_code(phone)
        return False
    if otp != code:
        await _increment_attempts(phone)
        return False

    await delete_code(phone)
    await _clear_attempts(phone)
    return True


async def _get_attempts(phone: str) -> int:
    try:
        redis = await _get_redis()
        raw = await redis.get(f"{settings.REDIS_PREFIX}otp_attempts:{phone}")
        await redis.aclose()
        return int(raw) if raw else 0
    except Exception:
        return _attempt_store.get(phone, 0)


async def _increment_attempts(phone: str) -> None:
    count = await _get_attempts(phone) + 1
    try:
        redis = await _get_redis()
        await redis.setex(f"{settings.REDIS_PREFIX}otp_attempts:{phone}", TTL_SECONDS, str(count))
        await redis.aclose()
    except Exception:
        _attempt_store[phone] = count


async def _clear_attempts(phone: str) -> None:
    try:
        redis = await _get_redis()
        await redis.delete(f"{settings.REDIS_PREFIX}otp_attempts:{phone}")
        await redis.aclose()
    except Exception:
        pass
    _attempt_store.pop(phone, None)


async def _get_stored(phone: str) -> tuple[str, datetime] | None:
    try:
        redis = await _get_redis()
        raw = await redis.get(_redis_key(phone))
        await redis.aclose()
        if not raw:
            return None
        data = json.loads(raw)
        return data["code"], datetime.fromisoformat(data["expires_at"])
    except Exception:
        entry = _memory_store.get(phone)
        return entry


async def delete_code(phone: str) -> None:
    try:
        redis = await _get_redis()
        await redis.delete(_redis_key(phone))
        await redis.aclose()
    except Exception:
        pass
    _memory_store.pop(phone, None)
