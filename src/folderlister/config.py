"""Configuración persistente durante una sesión, sin archivos de preferencias."""

from dataclasses import dataclass
from pathlib import Path

from folderlister.models import ElementKind, Representation, Result


@dataclass(slots=True)
class Session:
    """Opciones activas y último proceso completado."""

    root: Path | None = None
    recursive: bool = False
    kind: ElementKind = ElementKind.BOTH
    representation: Representation = Representation.RELATIVE
    last_result: Result | None = None
