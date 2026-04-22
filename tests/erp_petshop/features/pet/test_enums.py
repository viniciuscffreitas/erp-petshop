from __future__ import annotations

from erp_petshop.features.pet.enums import Especie


def test_especie_values_sao_estaveis() -> None:
    assert Especie.CAO.value == "cao"
    assert Especie.GATO.value == "gato"


def test_especie_e_string_enum() -> None:
    assert isinstance(Especie.CAO, str)
    assert Especie.CAO == "cao"


def test_especie_tem_exatamente_dois_membros() -> None:
    assert {e.value for e in Especie} == {"cao", "gato"}


def test_especie_construtor_a_partir_de_string() -> None:
    assert Especie("cao") is Especie.CAO
    assert Especie("gato") is Especie.GATO
