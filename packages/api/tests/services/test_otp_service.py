"""OTP service unit tests."""

import pytest

from app.services import otp_service


@pytest.mark.asyncio
async def test_store_and_verify_code():
    phone = "+5511999000001"
    code = await otp_service.store_code(phone, "123456")
    assert code == "123456"
    assert await otp_service.verify_code(phone, "123456") is True
    assert await otp_service.verify_code(phone, "123456") is False


@pytest.mark.asyncio
async def test_verify_wrong_code():
    phone = "+5511999000002"
    await otp_service.store_code(phone, "654321")
    assert await otp_service.verify_code(phone, "000000") is False


@pytest.mark.asyncio
async def test_max_attempts_blocks_verification():
    phone = "+5511999000003"
    await otp_service.store_code(phone, "111111")
    for _ in range(5):
        await otp_service.verify_code(phone, "999999")
    assert await otp_service.verify_code(phone, "111111") is False
