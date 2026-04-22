from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from erp_petshop.features.cliente.schemas import ClienteCreate, ClienteRead, ClienteUpdate


class TestClienteCreate:
    def test_aceita_telefone_apenas(self) -> None:
        c = ClienteCreate(nome="Maria", telefone="11999999999")
        assert c.nome == "Maria"
        assert c.telefone == "11999999999"
        assert c.email is None

    def test_aceita_email_apenas(self) -> None:
        c = ClienteCreate(nome="Joao", email="joao@example.com")
        assert c.email == "joao@example.com"
        assert c.telefone is None

    def test_aceita_ambos_canais(self) -> None:
        c = ClienteCreate(nome="Ana", telefone="+5511988887777", email="ana@ex.com")
        assert c.telefone == "+5511988887777"
        assert c.email == "ana@ex.com"

    def test_rejeita_nenhum_canal(self) -> None:
        with pytest.raises(ValidationError) as exc:
            ClienteCreate(nome="SemCanal")
        assert "cliente precisa de telefone ou email" in str(exc.value)

    def test_rejeita_nome_vazio(self) -> None:
        with pytest.raises(ValidationError):
            ClienteCreate(nome="", telefone="11999999999")

    def test_rejeita_nome_muito_longo(self) -> None:
        with pytest.raises(ValidationError):
            ClienteCreate(nome="x" * 101, telefone="11999999999")

    def test_aceita_nome_no_limite(self) -> None:
        ClienteCreate(nome="x" * 100, telefone="11999999999")

    def test_rejeita_telefone_com_letras(self) -> None:
        with pytest.raises(ValidationError):
            ClienteCreate(nome="X", telefone="abc123")

    def test_rejeita_telefone_muito_curto(self) -> None:
        with pytest.raises(ValidationError):
            ClienteCreate(nome="X", telefone="1234567")

    def test_aceita_telefone_e164(self) -> None:
        c = ClienteCreate(nome="X", telefone="+551188887777")
        assert c.telefone == "+551188887777"

    def test_rejeita_observacoes_acima_do_limite(self) -> None:
        with pytest.raises(ValidationError):
            ClienteCreate(nome="X", telefone="11999999999", observacoes="x" * 1001)

    def test_aceita_observacoes_no_limite(self) -> None:
        ClienteCreate(nome="X", telefone="11999999999", observacoes="x" * 1000)

    def test_rejeita_email_invalido(self) -> None:
        with pytest.raises(ValidationError):
            ClienteCreate(nome="X", email="nao-e-email")


class TestClienteUpdate:
    def test_todos_campos_opcionais(self) -> None:
        u = ClienteUpdate()
        assert u.nome is None
        assert u.telefone is None
        assert u.email is None
        assert u.observacoes is None

    def test_update_parcial_nome(self) -> None:
        u = ClienteUpdate(nome="Novo Nome")
        assert u.nome == "Novo Nome"

    def test_rejeita_nome_vazio(self) -> None:
        with pytest.raises(ValidationError):
            ClienteUpdate(nome="")

    def test_rejeita_telefone_invalido(self) -> None:
        with pytest.raises(ValidationError):
            ClienteUpdate(telefone="xyz")


class TestClienteRead:
    def test_serializa_from_attributes(self) -> None:
        class Row:
            id = uuid4()
            nome = "Maria"
            telefone = "11999999999"
            email = None
            observacoes = None
            created_at = datetime(2026, 4, 22, tzinfo=UTC)
            updated_at = datetime(2026, 4, 22, tzinfo=UTC)

        r = ClienteRead.model_validate(Row())
        assert r.nome == "Maria"
        assert r.telefone == "11999999999"
        assert r.email is None
