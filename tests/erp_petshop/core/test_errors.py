from __future__ import annotations

import pytest

from erp_petshop.core.errors import BusinessError, ConflictError, NotFoundError


def test_not_found_inherits_business_error() -> None:
    assert issubclass(NotFoundError, BusinessError)


def test_conflict_inherits_business_error() -> None:
    assert issubclass(ConflictError, BusinessError)


def test_business_error_is_exception() -> None:
    assert issubclass(BusinessError, Exception)


def test_raising_not_found_propagates_message() -> None:
    with pytest.raises(NotFoundError, match="cliente nao existe"):
        raise NotFoundError("cliente nao existe")


def test_raising_conflict_propagates_message() -> None:
    with pytest.raises(ConflictError, match="slot ocupado"):
        raise ConflictError("slot ocupado")


def test_conflict_is_not_not_found() -> None:
    assert not issubclass(ConflictError, NotFoundError)
    assert not issubclass(NotFoundError, ConflictError)
