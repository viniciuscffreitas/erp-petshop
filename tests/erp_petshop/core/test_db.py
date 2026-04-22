from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from erp_petshop.core.db import Base, SessionFactory, engine, get_session


def test_base_is_declarative() -> None:
    assert issubclass(Base, DeclarativeBase)


def test_engine_uses_configured_url() -> None:
    url = str(engine.url)
    assert url.startswith("sqlite+aiosqlite")


async def test_session_factory_creates_async_session() -> None:
    async with SessionFactory() as session:
        assert isinstance(session, AsyncSession)
        assert session.sync_session.expire_on_commit is False


async def test_get_session_yields_async_session() -> None:
    gen = get_session()
    session = await anext(gen)
    try:
        assert isinstance(session, AsyncSession)
    finally:
        await gen.aclose()
