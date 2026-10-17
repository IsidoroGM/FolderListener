"""Representaciones compartidas y nombres seguros para los resultados."""

import re
from pathlib import Path, PurePath

from folderlister.models import Entry, Representation


def output_stem(root: PurePath) -> str:
    """Normaliza incluso raíces de unidad, UNC y raíz POSIX."""
    name = root.name or root.drive or "raiz"
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip(" ._") or "raiz"
    # Deja espacio para sufijos y extensiones en sistemas con NAME_MAX=255 bytes.
    while len(name.encode("utf-8", errors="surrogatepass")) > 180:
        name = name[:-1]
    return name


def output_paths(root: Path) -> tuple[Path, Path, Path]:
    """Devuelve TXT, XLSX y registro reservados para esta raíz."""
    stem = output_stem(root)
    return (
        root / f"{stem}_listado.txt",
        root / f"{stem}_listado.xlsx",
        root / f"{stem}_errores.log",
    )


def render(entry: Entry, representation: Representation) -> str:
    """Representa una entrada; el árbol identifica carpetas solo de contexto."""
    if representation == Representation.NAME:
        return entry.path.name
    if representation == Representation.ABSOLUTE:
        return str(entry.path)
    if representation == Representation.RELATIVE:
        return str(entry.relative)
    prefix = "".join("    " if last else "│   " for last in entry.branches[:-1])
    connector = "└── " if entry.branches[-1] else "├── "
    suffix = "/" if entry.is_directory else ""
    context = " [contexto; no incluido]" if not entry.included else ""
    return prefix + connector + entry.path.name + suffix + context
