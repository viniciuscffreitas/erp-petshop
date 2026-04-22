"""Importability smoke test for all package __init__ markers.

Covers every `__init__.py` in the source tree with a single assertion: the
module can be imported. Empty package markers have no behavior to assert
beyond this; a failure here means the package structure itself is broken.
"""

from __future__ import annotations

import importlib
import pkgutil

import erp_petshop


def test_root_package_imports() -> None:
    assert erp_petshop.__name__ == "erp_petshop"


def test_all_subpackages_import() -> None:
    imported = []
    for info in pkgutil.walk_packages(erp_petshop.__path__, prefix="erp_petshop."):
        module = importlib.import_module(info.name)
        assert module.__name__ == info.name
        imported.append(info.name)
    assert imported, "no subpackages discovered under erp_petshop"
