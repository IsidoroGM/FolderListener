"""Validación y tres mecanismos de selección de directorios."""

import os
import stat
from collections.abc import Callable
from pathlib import Path

from folderlister.filesystem import directory_handle, safe_children
from folderlister.filters import excluded


def validate_directory(value: str | Path) -> Path:
    """Valida ruta absoluta, accesible y sin redirecciones en sus componentes."""
    path = Path(str(value).strip().strip('"')).expanduser()
    if not path.is_absolute():
        raise ValueError("Introduce una ruta absoluta.")
    if ".." in path.parts:
        raise ValueError("La ruta no puede contener '..'.")
    with directory_handle(path) as handle, os.scandir(handle):
        pass
    return path


def graphical_directory() -> Path | None:
    """Abre tkinter opcionalmente; RuntimeError permite volver a consola."""
    window = None
    try:
        import tkinter
        from tkinter import filedialog

        window = tkinter.Tk()
        window.withdraw()
        value = filedialog.askdirectory(title="Selecciona la carpeta que se va a listar")
        return validate_directory(value) if value else None
    except (ImportError, RuntimeError, OSError) as error:
        raise RuntimeError(f"Selector gráfico no disponible: {error}") from error
    except Exception as error:
        # TclError solo existe si tkinter se ha importado correctamente.
        if error.__class__.__name__ != "TclError":
            raise
        raise RuntimeError(f"No hay entorno gráfico disponible: {error}") from error
    finally:
        if window is not None:
            window.destroy()


def browse_directory(
    start: Path,
    read: Callable[[str], str] = input,
    write: Callable[[str], None] = print,
) -> Path | None:
    """Navega por carpetas; permite elegir, subir, cambiar unidad o cancelar."""
    current = validate_directory(start)
    while True:
        write(f"\nDirectorio: {current}")
        try:
            directories = sorted(
                (
                    name
                    for name, info in safe_children(current)
                    if stat.S_ISDIR(info.st_mode) and not excluded(name, info)
                ),
                key=lambda name: (name.casefold(), name),
            )
        except OSError as error:
            write(f"No se puede leer esta carpeta: {error}")
            directories = []
        for index, name in enumerate(directories, 1):
            write(f"{index}. {name}")
        answer = read("Número / e elegir / s subir / r otra ruta o unidad / 0 cancelar: ").strip()
        if answer == "0":
            return None
        try:
            if answer == "e":
                return validate_directory(current)
            if answer == "s":
                current = validate_directory(current.parent)
            elif answer == "r":
                current = validate_directory(read("Ruta absoluta: "))
            elif answer.isdecimal() and 1 <= int(answer) <= len(directories):
                current = validate_directory(current / directories[int(answer) - 1])
            else:
                write("Opción no válida.")
        except (ValueError, OSError) as error:
            write(f"No se puede seleccionar: {error}")
