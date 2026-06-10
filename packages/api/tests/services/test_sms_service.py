"""Unit tests for SMSService."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.sms_service import SMSService, get_sms_service


class TestSMSService:
    @pytest.fixture
    def sms_service(self):
        return SMSService()

    @pytest.fixture
    def mock_disabled(self):
        with patch("app.services.sms_service.get_cached_bool", return_value=False):
            with patch("app.services.sms_service.get_cached_setting", return_value=""):
                yield

    @pytest.fixture
    def mock_enabled_no_token(self):
        with patch("app.services.sms_service.get_cached_bool", return_value=True):
            with patch("app.services.sms_service.get_cached_setting", return_value=""):
                yield

    def test_properties(self, sms_service, mock_disabled):
        assert sms_service.api_url == "https://api.nvoip.com.br/v2"
        assert sms_service.enabled is False
        assert sms_service.token == ""
        assert sms_service.from_number == ""

    @pytest.mark.asyncio
    async def test_send_when_disabled(self, sms_service, mock_disabled):
        assert await sms_service.send("+5511999999999", "Hello") is True

    @pytest.mark.asyncio
    async def test_send_when_enabled_without_token(self, sms_service, mock_enabled_no_token):
        assert await sms_service.send("+5511999999999", "Hello") is False

    @pytest.mark.asyncio
    async def test_send_success(self, sms_service):
        with patch("app.services.sms_service.get_cached_bool", return_value=True):
            with patch("app.services.sms_service.get_cached_setting", return_value="token"):
                mock_response = AsyncMock()
                mock_response.status_code = 200
                mock_client = AsyncMock()
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)

                with patch("httpx.AsyncClient", return_value=mock_client):
                    assert await sms_service.send("+5511999999999", "Test") is True

    @pytest.mark.asyncio
    async def test_send_failure_status(self, sms_service):
        with patch("app.services.sms_service.get_cached_bool", return_value=True):
            with patch("app.services.sms_service.get_cached_setting", return_value="token"):
                mock_response = AsyncMock()
                mock_response.status_code = 500
                mock_response.text = "error"
                mock_client = AsyncMock()
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)

                with patch("httpx.AsyncClient", return_value=mock_client):
                    assert await sms_service.send("+5511999999999", "Test") is False

    @pytest.mark.asyncio
    async def test_helper_messages(self, sms_service, mock_disabled):
        assert await sms_service.send_verification_code("+5511999999999", "123456") is True
        assert (
            await sms_service.send_appointment_confirmation(
                "+5511999999999", "Barbearia", "2026-06-10", "10:00"
            )
            is True
        )
        assert (
            await sms_service.send_appointment_reminder("+5511999999999", "Barbearia", "10:00")
            is True
        )
        assert (
            await sms_service.send_appointment_cancelled(
                "+5511999999999", "Barbearia", reason="Chuva"
            )
            is True
        )
        assert (
            await sms_service.send_payment_received("+5511999999999", 50.0, "Barbearia") is True
        )

    def test_get_sms_service_singleton(self):
        import app.services.sms_service as sms_module

        sms_module._sms_service = None
        first = get_sms_service()
        second = get_sms_service()
        assert first is second
