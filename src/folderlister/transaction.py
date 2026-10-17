"""Preparación temporal y publicación recuperable de los archivos de salida."""

import os
import stat
import tempfile
from collections.abc import Callable
from pathlib import Path

from folderlister.filesystem import redirected
from folderlister.models import Cancelled


def fingerprint(path: Path) -> tuple[int, int, int, int] | None:
    """Identifica la versión observada y rechaza salidas especiales o enlazadas."""
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if redirected(info) or not stat.S_ISREG(info.st_mode):
        raise OSError(f"La salida no es un archivo regular seguro: {path}")
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


class OutputTransaction:
    """Conserva versiones antiguas hasta sustituir todas las salidas previstas."""

    def __init__(self, outputs: tuple[Path, ...], confirm: Callable[[tuple[Path, ...]], bool]):
        self.outputs = outputs
        self.before = {path: fingerprint(path) for path in outputs}
        existing = tuple(path for path in outputs if self.before[path] is not None)
        if existing and not confirm(existing):
            raise Cancelled("Sobrescritura rechazada.")
        self.temporary = tempfile.TemporaryDirectory(prefix=".folderlister-", dir=outputs[0].parent)
        self.work = Path(self.temporary.name)
        self.recovery_required = False

    def stage(self, output: Path) -> Path:
        """Ruta temporal para una salida propia."""
        return self.work / output.name

    def publish(self, outputs: tuple[Path, ...]) -> None:
        """Publica o restaura; rechaza cambios de terceros desde la confirmación."""
        for path in self.outputs:
            if fingerprint(path) != self.before[path]:
                raise OSError(f"La salida cambió durante el proceso; no se sobrescribe: {path}")
        backups: dict[Path, Path] = {}
        installed: list[Path] = []
        try:
            for path in outputs:
                staged = self.stage(path)
                with staged.open("r+b") as stream:
                    os.fsync(stream.fileno())
                if self.before[path] is not None:
                    backup = self.work / (path.name + ".backup")
                    os.replace(path, backup)
                    backups[path] = backup
                os.replace(staged, path)
                installed.append(path)
        except BaseException as original:
            try:
                for path in reversed(installed):
                    path.unlink()
                for path, backup in backups.items():
                    os.replace(backup, path)
            except OSError as recovery:
                self.recovery_required = True
                # No borrar la única copia recuperable ni en el finalizador.
                self.temporary._finalizer.detach()
                raise OSError(
                    f"Recuperación manual necesaria en {self.work}: {recovery}"
                ) from original
            raise

    def close(self) -> None:
        """Elimina solo el espacio temporal propio, salvo recuperación pendiente."""
        if not self.recovery_required:
            self.temporary.cleanup()
