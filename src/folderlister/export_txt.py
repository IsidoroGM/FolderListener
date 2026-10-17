"""Exportador de texto UTF-8 incremental."""

from datetime import datetime
from pathlib import Path

from folderlister import __version__
from folderlister.config import Session
from folderlister.models import Entry, Statistics
from folderlister.rendering import render


class TxtExporter:
    """Escribe cabecera, entradas y resumen sin almacenar el inventario."""

    def __init__(self, path: Path, root: Path, config: Session, started: datetime) -> None:
        self.stream = path.open("w", encoding="utf-8", errors="backslashreplace", newline="\n")
        self.config = config
        self.stream.write(
            f"FolderLister {__version__}\nDirectorio: {root}\n"
            f"Fecha: {started.isoformat(timespec='seconds')}\n"
            f"Exploración: {'recursiva' if config.recursive else 'primer nivel'}\n"
            f"Elementos: {config.kind.value}\nRepresentación: {config.representation.value}\n\n"
        )

    def append(self, entry: Entry) -> None:
        """Escribe una entrada o carpeta de contexto."""
        self.stream.write(render(entry, self.config.representation) + "\n")

    def preserve(self, path: Path, column: str, value: str) -> None:
        """Conserva valores completos cuando Excel necesita transformarlos."""
        self.stream.write(f"[Valor completo para Excel; {path!s}; {column}] {value}\n")

    def finish(self, statistics: Statistics) -> None:
        """Añade estado y contadores, incluso si no se incluyó ningún elemento."""
        if not statistics.directories_listed + statistics.files_listed:
            self.stream.write("No se encontraron elementos que cumplan las opciones.\n")
        self.stream.write(
            f"\nEstado: {'parcial / con advertencias' if statistics.issues else 'completo'}\n"
            f"Directorios explorados: {statistics.directories_scanned}\n"
            f"Carpetas listadas: {statistics.directories_listed}\n"
            f"Archivos listados: {statistics.files_listed}\n"
            f"Incidencias: {statistics.issues}\nDuración: {statistics.duration:.3f} s\n"
        )

    def close(self) -> None:
        """Cierra el archivo incluso después de un fallo."""
        self.stream.close()
