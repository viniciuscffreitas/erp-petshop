from __future__ import annotations

from uuid import UUID

from erp_petshop.core.db import Base
from erp_petshop.features.pet.enums import Especie
from erp_petshop.features.pet.models import Pet


def test_pet_is_mapped_on_base() -> None:
    assert Pet.__tablename__ == "pet"
    assert "pet" in Base.metadata.tables


def test_pet_columns_match_design() -> None:
    cols = {c.name for c in Pet.__table__.columns}
    assert cols == {
        "id",
        "nome",
        "especie",
        "raca",
        "observacoes",
        "cliente_id",
        "created_at",
        "updated_at",
    }


def test_pet_pk_is_id() -> None:
    pk = [c.name for c in Pet.__table__.primary_key.columns]
    assert pk == ["id"]


def test_pet_nome_constrained_to_60() -> None:
    col = Pet.__table__.columns["nome"]
    assert not col.nullable
    assert col.type.length == 60


def test_pet_raca_nullable_and_size_80() -> None:
    col = Pet.__table__.columns["raca"]
    assert col.nullable
    assert col.type.length == 80


def test_pet_observacoes_nullable_and_size_1000() -> None:
    col = Pet.__table__.columns["observacoes"]
    assert col.nullable
    assert col.type.length == 1000


def test_pet_cliente_id_has_fk_restrict() -> None:
    col = Pet.__table__.columns["cliente_id"]
    assert not col.nullable
    fks = list(col.foreign_keys)
    assert len(fks) == 1
    fk = fks[0]
    assert fk.column.table.name == "cliente"
    assert fk.column.name == "id"
    assert fk.ondelete == "RESTRICT"


def test_pet_cliente_id_is_indexed() -> None:
    col = Pet.__table__.columns["cliente_id"]
    assert col.index is True


def test_pet_especie_uses_sql_enum() -> None:
    col = Pet.__table__.columns["especie"]
    assert set(col.type.enums) == {"cao", "gato"}


def test_pet_instance_accepts_values() -> None:
    cid = UUID("00000000-0000-0000-0000-000000000001")
    p = Pet(nome="Rex", especie=Especie.CAO, cliente_id=cid)
    assert p.nome == "Rex"
    assert p.especie is Especie.CAO
    assert p.cliente_id == cid
