"""Prueba de integración real de un ejecutable empaquetado."""

import subprocess
import sys
import tempfile
from pathlib import Path

from openpyxl import load_workbook


def main() -> None:
    """Ejecuta el menú, verifica salidas y rechaza una segunda sobrescritura."""
    executable = Path(sys.argv[1]).resolve()
    with tempfile.TemporaryDirectory(prefix="folderlister-smoke-ñ-") as directory:
        root = Path(directory).resolve()
        (root / "Carpeta ñ").mkdir()
        (root / "Carpeta ñ" / "Documento.txt").write_text("no leer", encoding="utf-8")
        (root / "=1+1.txt").touch()
        answers = f"1\n1\n{root}\n2\n2\n4\n4\n5\ns\ns\n0\n"
        process = subprocess.run(
            [str(executable)],
            input=answers,
            encoding="utf-8",
            capture_output=True,
            timeout=90,
            check=True,
        )
        assert "Resultado completo" in process.stdout, process.stdout + process.stderr
        txt = next(root.glob("*_listado.txt"))
        xlsx = next(root.glob("*_listado.xlsx"))
        assert "Documento.txt" in txt.read_text(encoding="utf-8")
        book = load_workbook(xlsx, read_only=True)
        assert len(list(book["Elementos"].values)) == 4
        book.close()
        before = (txt.read_bytes(), xlsx.read_bytes())
        subprocess.run(
            [str(executable)],
            input=f"1\n1\n{root}\n5\ns\nn\n0\n",
            encoding="utf-8",
            capture_output=True,
            timeout=90,
            check=True,
        )
        assert before == (txt.read_bytes(), xlsx.read_bytes())
        assert not list(root.glob(".folderlister-*"))
    print("Smoke test del ejecutable: correcto.")


if __name__ == "__main__":
    main()
