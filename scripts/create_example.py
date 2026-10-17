"""Crea un ejemplo pequeño dentro del proyecto y genera salidas auténticas."""

from pathlib import Path

from folderlister.config import Session
from folderlister.controller import generate
from folderlister.models import Representation


def main() -> None:
    """Genera exclusivamente el ejemplo propio, nunca una ruta de usuario."""
    root = Path(__file__).resolve().parents[1] / "examples" / "Proyectos"
    for name in ("Proyecto_A", "Proyecto_B"):
        (root / name).mkdir(parents=True, exist_ok=True)
    for relative in ("Proyecto_A/Documento.txt", "Proyecto_B/Datos.csv", "Notas con acentos ñ.txt"):
        (root / relative).touch(exist_ok=True)
    result = generate(
        Session(root=root, recursive=True, representation=Representation.TREE),
        confirm_overwrite=lambda paths: True,
    )
    print("\n".join(str(path) for path in result.outputs))


if __name__ == "__main__":
    main()
