from __future__ import annotations

from uuid import UUID

from erp_petshop.core.db import Base
from erp_petshop.features.cliente.models import Cliente


def test_cliente_is_mapped_on_base() -> None:
    assert Cliente.__tablename__ == "cliente"
    assert "cliente" in Base.metadata.tables


def test_cliente_columns_match_design() -> None:
    cols = {c.name: c for c in Cliente.__table__.columns}
    assert set(cols) == {
        "id",
        "nome",
        "telefone",
        "email",
        "observacoes",
        "created_at",
        "updated_at",
    }


def test_cliente_pk_is_id() -> None:
    pk = [c.name for c in Cliente.__table__.primary_key.columns]
    assert pk == ["id"]


def test_cliente_nome_not_nullable_and_size_100() -> None:
    col = Cliente.__table__.columns["nome"]
    assert not col.nullable
    assert col.type.length == 100


def test_cliente_telefone_nullable_and_size_20() -> None:
    col = Cliente.__table__.columns["telefone"]
    assert col.nullable
    assert col.type.length == 20


def test_cliente_email_nullable_and_size_120() -> None:
    col = Cliente.__table__.columns["email"]
    assert col.nullable
    assert col.type.length == 120


def test_cliente_observacoes_nullable_and_size_1000() -> None:
    col = Cliente.__table__.columns["observacoes"]
    assert col.nullable
    assert col.type.length == 1000


def test_cliente_has_timestamps() -> None:
    assert Cliente.__table__.columns["created_at"].server_default is not None
    assert Cliente.__table__.columns["updated_at"].server_default is not None
    assert Cliente.__table__.columns["updated_at"].onupdate is not None


def test_cliente_instance_accepts_explicit_uuid() -> None:
    uid = UUID("11111111-2222-3333-4444-555555555555")
    c = Cliente(id=uid, nome="Maria", telefone="11999999999")
    assert c.id == uid
    assert c.nome == "Maria"
