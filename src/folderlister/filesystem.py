"""Aperturas de directorios que rechazan redirecciones del sistema de archivos."""

import os
import stat
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


def redirected(info: os.stat_result) -> bool:
    """Detecta symlinks y cualquier reparse point de Windows."""
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


@contextmanager
def directory_handle(path: Path) -> Iterator[int | Path]:
    """Fija cada componente de una ruta absoluta sin seguir enlaces."""
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError("Se requiere una ruta absoluta sin componentes '..'.")
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        create = kernel.CreateFileW
        create.argtypes = [
            wintypes.LPCWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            ctypes.c_void_p,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.HANDLE,
        ]
        create.restype = wintypes.HANDLE
        close = kernel.CloseHandle
        close.argtypes = [wintypes.HANDLE]
        close.restype = wintypes.BOOL
        handles = []
        current = Path(path.anchor)
        try:
            for part in (None, *path.parts[1:]):
                if part is not None:
                    current /= part
                handle = create(str(current), 0x80, 3, None, 3, 0x02200000, None)
                if handle == wintypes.HANDLE(-1).value:
                    error = ctypes.WinError(ctypes.get_last_error())
                    raise OSError(f"No se puede fijar el directorio {current}: {error}") from error
                handles.append(handle)
                info = current.lstat()
                if redirected(info) or not stat.S_ISDIR(info.st_mode):
                    raise OSError(f"Directorio redirigido o no válido: {current}")
            yield path
        finally:
            for handle in reversed(handles):
                close(handle)
    else:
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        descriptor = os.open(path.anchor, flags)
        try:
            for part in path.parts[1:]:
                next_descriptor = os.open(part, flags, dir_fd=descriptor)
                os.close(descriptor)
                descriptor = next_descriptor
            yield descriptor
        finally:
            os.close(descriptor)


def safe_children(path: Path) -> list[tuple[str, os.stat_result]]:
    """Lee únicamente nombres y metadatos bajo una apertura protegida."""
    with directory_handle(path) as handle, os.scandir(handle) as children:
        return [(child.name, child.stat(follow_symlinks=False)) for child in children]


def directory_identity(handle: int | Path) -> tuple[int, int]:
    """Identidad física para detectar ciclos de montajes en la rama activa."""
    info = os.fstat(handle) if isinstance(handle, int) else handle.stat(follow_symlinks=False)
    return info.st_dev, info.st_ino
