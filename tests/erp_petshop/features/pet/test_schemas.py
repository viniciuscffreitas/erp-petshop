from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from erp_petshop.features.pet.enums import Especie
from erp_petshop.features.pet.schemas import PetCreate, PetRead, PetUpdate


class TestPetCreate:
    def test_aceita_minimo(self) -> None:
        cid = uuid4()
        p = PetCreate(nome="Rex", especie=Especie.CAO, cliente_id=cid)
        assert p.nome == "Rex"
        assert p.especie is Especie.CAO
        assert p.raca is None
        assert p.observacoes is None
        assert p.cliente_id == cid

    def test_aceita_completo(self) -> None:
        p = PetCreate(
            nome="Miau",
            especie=Especie.GATO,
            raca="Persa",
            observacoes="dorme muito",
            cliente_id=uuid4(),
        )
        assert p.raca == "Persa"
        assert p.observacoes == "dorme muito"

    def test_rejeita_especie_fora_do_enum(self) -> None:
        with pytest.raises(ValidationError):
            PetCreate(nome="X", especie="peixe", cliente_id=uuid4())  # type: ignore[arg-type]

    def test_rejeita_nome_vazio(self) -> None:
        with pytest.raises(ValidationError):
            PetCreate(nome="", especie=Especie.CAO, cliente_id=uuid4())

    def test_rejeita_nome_muito_longo(self) -> None:
        with pytest.raises(ValidationError):
            PetCreate(nome="x" * 61, especie=Especie.CAO, cliente_id=uuid4())

    def test_aceita_nome_no_limite(self) -> None:
        PetCreate(nome="x" * 60, especie=Especie.CAO, cliente_id=uuid4())

    def test_rejeita_raca_muito_longa(self) -> None:
        with pytest.raises(ValidationError):
            PetCreate(
                nome="X",
                especie=Especie.CAO,
                raca="y" * 81,
                cliente_id=uuid4(),
            )

    def test_aceita_raca_no_limite(self) -> None:
        PetCreate(
            nome="X",
            especie=Especie.CAO,
            raca="y" * 80,
            cliente_id=uuid4(),
        )

    def test_rejeita_observacoes_muito_longas(self) -> None:
        with pytest.raises(ValidationError):
            PetCreate(
                nome="X",
                especie=Especie.CAO,
                cliente_id=uuid4(),
                observacoes="x" * 1001,
            )

    def test_rejeita_cliente_id_ausente(self) -> None:
        with pytest.raises(ValidationError):
            PetCreate(nome="X", especie=Especie.CAO)  # type: ignore[call-arg]

    def test_rejeita_cliente_id_string_invalida(self) -> None:
        with pytest.raises(ValidationError):
            PetCreate(nome="X", especie=Especie.CAO, cliente_id="nao-e-uuid")  # type: ignore[arg-type]


class TestPetUpdate:
    def test_todos_opcionais(self) -> None:
        u = PetUpdate()
        assert u.nome is None
        assert u.especie is None
        assert u.raca is None
        assert u.observacoes is None

    def test_update_parcial_especie(self) -> None:
        u = PetUpdate(especie=Especie.GATO)
        assert u.especie is Especie.GATO

    def test_rejeita_especie_fora_do_enum(self) -> None:
        with pytest.raises(ValidationError):
            PetUpdate(especie="cobra")  # type: ignore[arg-type]

    def test_rejeita_nome_vazio(self) -> None:
        with pytest.raises(ValidationError):
            PetUpdate(nome="")


class TestPetRead:
    def test_serializa_from_attributes(self) -> None:
        class Row:
            id = uuid4()
            nome = "Rex"
            especie = Especie.CAO
            raca = None
            observacoes = None
            cliente_id = uuid4()
            created_at = datetime(2026, 4, 22, tzinfo=UTC)
            updated_at = datetime(2026, 4, 22, tzinfo=UTC)

        r = PetRead.model_validate(Row())
        assert r.nome == "Rex"
        assert r.especie is Especie.CAO
