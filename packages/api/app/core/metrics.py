"""In-process request metrics for observability."""

import time
from dataclasses import dataclass

_start_time = time.monotonic()
_requests_total = 0
_requests_4xx = 0
_requests_5xx = 0
_active_requests = 0


@dataclass
class MetricsSnapshot:
    uptime_seconds: float
    requests_total: int
    requests_4xx: int
    requests_5xx: int
    active_requests: int


def record_request_start() -> None:
    global _active_requests
    _active_requests += 1


def record_request_end(status_code: int) -> None:
    global _requests_total, _requests_4xx, _requests_5xx, _active_requests
    _requests_total += 1
    if status_code >= 500:
        _requests_5xx += 1
    elif status_code >= 400:
        _requests_4xx += 1
    _active_requests = max(0, _active_requests - 1)


def get_metrics() -> MetricsSnapshot:
    return MetricsSnapshot(
        uptime_seconds=round(time.monotonic() - _start_time, 2),
        requests_total=_requests_total,
        requests_4xx=_requests_4xx,
        requests_5xx=_requests_5xx,
        active_requests=_active_requests,
    )
