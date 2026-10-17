"""Fixtures de árboles pequeños con nombres representativos."""

import pytest


@pytest.fixture
def tmp_path(tmp_path):
    """Usa la ruta física del temporal (macOS suele enlazar /var y /tmp)."""
    return tmp_path.resolve()


@pytest.fixture
def tree(tmp_path):
    root = tmp_path / "Inventario ñ"
    root.mkdir()
    (root / "beta").mkdir()
    (root / "Árbol").mkdir()
    (root / "beta" / "sub").mkdir()
    (root / "beta" / "sub" / "profundo.txt").write_text("no leer", encoding="utf-8")
    (root / "beta" / "Z.txt").touch()
    (root / "A con espacios.txt").touch()
    (root / "z.txt").touch()
    (root / ".oculto").mkdir()
    (root / ".oculto" / "secreto.txt").touch()
    (root / ".archivo").touch()
    return root
