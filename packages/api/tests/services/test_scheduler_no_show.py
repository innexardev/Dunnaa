"""Auto no-show scheduler tests."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.models.appointment import AppointmentStatus
from app.services.scheduler import mark_auto_no_shows


@pytest.mark.asyncio
async def test_mark_auto_no_shows_empty():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    mock_db.__aenter__.return_value = mock_db
    mock_db.__aexit__.return_value = None

    with patch("app.services.scheduler.async_session_factory", return_value=mock_db):
        count = await mark_auto_no_shows()
        assert count == 0


@pytest.mark.asyncio
async def test_mark_auto_no_shows_marks_late_appointment():
    mock_appt = MagicMock()
    mock_appt.id = uuid4()
    mock_appt.status = AppointmentStatus.confirmed
    mock_appt.scheduled_at = datetime.now(UTC) - timedelta(hours=2)

    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_appt]
    mock_db.execute.return_value = mock_result
    mock_db.__aenter__.return_value = mock_db
    mock_db.__aexit__.return_value = None

    with patch("app.services.scheduler.async_session_factory", return_value=mock_db):
        with patch("app.services.appointment_service.AppointmentService") as MockSvc:
            instance = MockSvc.return_value
            instance.mark_no_show = AsyncMock(return_value=True)
            count = await mark_auto_no_shows()
            assert count == 1
            instance.mark_no_show.assert_called_once_with(mock_appt.id)
