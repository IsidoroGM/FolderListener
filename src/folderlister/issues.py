"""Registro incremental de incidencias sin acumular mensajes en memoria."""

import logging
from pathlib import Path

from folderlister.models import Statistics


class IssueLog:
    """Abre el log únicamente cuando se produce una incidencia."""

    def __init__(self, path: Path, statistics: Statistics) -> None:
        self.path = path
        self.statistics = statistics
        self.logger = logging.Logger(f"folderlister.{id(self)}", logging.WARNING)
        self.handler: logging.FileHandler | None = None

    def record(self, path: Path, operation: str, error: object) -> None:
        """Registra ruta, operación, fecha y explicación sin leer contenidos."""
        if self.handler is None:
            self.handler = logging.FileHandler(
                self.path, encoding="utf-8", errors="backslashreplace"
            )
            self.handler.setFormatter(
                logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
            )
            self.logger.addHandler(self.handler)
        self.statistics.issues += 1
        # repr impide que saltos de línea en nombres falsifiquen líneas del log.
        self.logger.warning("%r | %s | %r", str(path), operation, error)

    def close(self) -> None:
        """Libera el descriptor de registro."""
        if self.handler is not None:
            self.handler.close()
            self.logger.removeHandler(self.handler)
