"""Modelos compartidos entre exploración, consola y exportación."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path


class ElementKind(StrEnum):
    """Tipos de elementos solicitables."""

    DIRECTORIES = "carpetas"
    FILES = "archivos"
    BOTH = "carpetas y archivos"


class Representation(StrEnum):
    """Representaciones del inventario."""

    NAME = "nombre"
    ABSOLUTE = "ruta absoluta"
    RELATIVE = "ruta relativa"
    TREE = "árbol"


@dataclass(frozen=True, slots=True)
class Entry:
    """Una entrada; las carpetas de contexto no cuentan como resultados."""

    path: Path
    relative: Path
    is_directory: bool
    included: bool
    branches: tuple[bool, ...]  # True indica último hermano visible.

    @property
    def depth(self) -> int:
        """Profundidad: hijos inmediatos de la raíz = 1."""
        return len(self.relative.parts)


@dataclass(slots=True)
class Statistics:
    """Contadores acumulados, sin conservar las entradas."""

    directories_scanned: int = 0
    directories_listed: int = 0
    files_listed: int = 0
    issues: int = 0
    duration: float = 0.0


@dataclass(frozen=True, slots=True)
class Result:
    """Resultado de una publicación finalizada."""

    root: Path
    started: datetime
    statistics: Statistics
    outputs: tuple[Path, ...]

    @property
    def partial(self) -> bool:
        """Indica omisiones o advertencias en el resultado."""
        return self.statistics.issues > 0


class Cancelled(Exception):
    """Cancelación solicitada antes de publicar resultados."""
