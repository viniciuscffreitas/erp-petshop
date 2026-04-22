from __future__ import annotations

import pytest

from erp_petshop.core.config import Settings


def test_defaults_when_no_env() -> None:
    s = Settings(_env_file=None)
    assert s.slot_minutes == 30
    assert s.retro_tolerance_minutes == 5
    assert s.jwt_algorithm == "HS256"
    assert s.jwt_expire_minutes == 480
    assert s.database_url.startswith("sqlite+aiosqlite")


def test_env_override_slot_and_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SLOT_MINUTES", "15")
    monkeypatch.setenv("JWT_SECRET", "unit-secret")
    s = Settings(_env_file=None)
    assert s.slot_minutes == 15
    assert s.jwt_secret == "unit-secret"


def test_extra_env_is_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UNRELATED_VAR", "noise")
    Settings(_env_file=None)
