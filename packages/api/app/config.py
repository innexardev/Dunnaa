"""Deprecated shim — use ``app.core.config`` instead."""

from app.core.config import AppMode, Settings, get_settings, settings

__all__ = ["AppMode", "Settings", "get_settings", "settings"]
