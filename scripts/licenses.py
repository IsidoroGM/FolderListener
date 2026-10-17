"""Recoge licencias instaladas sin acceder a la red ni inventar permisos."""

import importlib.metadata
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Guarda metadatos y textos de terceros para revisión de cada compilación."""
    destination = ROOT / "dist" / "THIRD_PARTY_NOTICES"
    destination.mkdir(parents=True, exist_ok=True)
    supplied = ROOT / "licenses"
    if supplied.exists():
        shutil.copytree(supplied, destination / "supplemental", dirs_exist_ok=True)
    records = []
    for distribution in sorted(
        importlib.metadata.distributions(), key=lambda item: item.metadata["Name"]
    ):
        name = distribution.metadata["Name"]
        if name.casefold() == "folderlister":
            continue
        texts = []
        for file in distribution.files or []:
            if any(
                word in file.name.lower()
                for word in ("license", "licence", "copying", "copyright", "notice")
            ):
                source = Path(distribution.locate_file(file))
                if source.is_file() and source.suffix not in (".py", ".pyc"):
                    target = destination / name / Path(str(file))
                    if ".." in file.parts:
                        continue
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)
                    texts.append(str(target.relative_to(destination)))
        records.append(
            {
                "name": name,
                "version": distribution.version,
                "license": distribution.metadata.get("License-Expression")
                or distribution.metadata.get("License", "No declarada"),
                "texts": texts,
            }
        )
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if python_license.exists():
        shutil.copy2(python_license, destination / "Python-LICENSE.txt")
    # Tcl/Tk suele distribuir sus avisos junto a init.tcl; incluirlos si están presentes.
    for library in (Path(sys.base_prefix) / "tcl", Path(sys.base_prefix) / "lib"):
        if library.exists():
            for source in library.glob("**/license.terms"):
                target = destination / "TclTk" / source.relative_to(library)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
    (destination / "inventory.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
