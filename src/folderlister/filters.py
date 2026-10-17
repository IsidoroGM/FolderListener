"""Política uniforme para nombres, atributos y tipos de archivo."""

import os
import stat

from folderlister.filesystem import redirected


def excluded(name: str, info: os.stat_result) -> bool:
    """Excluye ocultos Unix/macOS/Windows, enlaces y archivos especiales."""
    return (
        name.startswith(".")
        or bool(getattr(info, "st_file_attributes", 0) & (0x2 | 0x4))
        or bool(getattr(info, "st_flags", 0) & getattr(stat, "UF_HIDDEN", 0x8000))
        or redirected(info)
        or not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode))
    )
