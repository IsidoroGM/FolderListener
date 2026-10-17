"""Menú interactivo en español y punto de entrada de FolderLister."""

import argparse
import sys
from collections.abc import Callable
from pathlib import Path

from folderlister import __version__
from folderlister.config import Session
from folderlister.controller import generate
from folderlister.models import Cancelled, ElementKind, Representation, Result
from folderlister.selection import browse_directory, graphical_directory, validate_directory


def summary(result: Result) -> str:
    """Resumen legible del último proceso publicado."""
    stats = result.statistics
    return (
        f"Resultado {'parcial / con advertencias' if result.partial else 'completo'}\n"
        f"Directorio: {result.root}\nFecha: {result.started.isoformat(timespec='seconds')}\n"
        f"Directorios explorados: {stats.directories_scanned}\n"
        f"Carpetas: {stats.directories_listed}; archivos: {stats.files_listed}; "
        f"incidencias: {stats.issues}\n"
        f"Duración de exploración y filas: {stats.duration:.3f} s\n"
        + "\n".join(f"Guardado: {path}" for path in result.outputs)
    )


def run_menu(
    session: Session | None = None,
    read: Callable[[str], str] = input,
    write: Callable[[str], None] = print,
) -> int:
    """Mantiene la sesión; EOF sale y Ctrl+C cancela la operación actual."""
    config = session if session is not None else Session()

    def choose(prompt: str, choices: list):
        for index, choice in enumerate(choices, 1):
            write(f"{index}. {choice}")
        while True:
            answer = read(prompt + " (0 cancelar): ").strip()
            if answer == "0":
                return None
            if answer.isdecimal() and 1 <= int(answer) <= len(choices):
                return choices[int(answer) - 1]
            write("Opción no válida.")

    def yes(prompt: str) -> bool:
        while True:
            answer = read(prompt + " [s/N]: ").strip().casefold()
            if answer in ("s", "sí", "si"):
                return True
            if answer in ("", "n", "no"):
                return False
            write("Responde s o n.")

    def overwrite(paths: tuple[Path, ...]) -> bool:
        write("Ya existen estas salidas (el log anterior se conserva si no hay incidencias):")
        for path in paths:
            write(str(path))
        return yes("¿Autorizas sobrescribir las salidas que se generen?")

    while True:
        try:
            write(
                f"\nFolderLister {__version__}\nDirectorio: {config.root or '(sin seleccionar)'}\n"
                f"Profundidad: {'recursiva' if config.recursive else 'primer nivel'} | "
                f"Elementos: {config.kind.value} | Formato: {config.representation.value}\n"
                "1. Seleccionar directorio.\n2. Configurar profundidad de búsqueda.\n"
                "3. Elegir elementos que se van a listar.\n"
                "4. Elegir formato de representación.\n5. Generar listado.\n"
                "6. Consultar resumen del último proceso.\n0. Salir."
            )
            action = read("Opción: ").strip()
            if action == "0":
                return 0
            if action == "1":
                mechanism = choose(
                    "Mecanismo", ["Ruta absoluta", "Navegar por consola", "Selector gráfico"]
                )
                selected = None
                if mechanism == "Ruta absoluta":
                    value = read("Ruta absoluta (vacío cancela): ").strip()
                    if value:
                        selected = validate_directory(value)
                elif mechanism == "Navegar por consola":
                    selected = browse_directory(config.root or Path.cwd(), read, write)
                elif mechanism == "Selector gráfico":
                    try:
                        selected = graphical_directory()
                    except RuntimeError as error:
                        write(str(error) + ". Puedes continuar con una ruta en consola.")
                        value = read("Ruta absoluta (vacío cancela): ").strip()
                        if value:
                            selected = validate_directory(value)
                if selected is not None:
                    config.root = selected
            elif action == "2":
                depth = choose("Profundidad", ["Primer nivel", "Recursiva"])
                if depth is not None:
                    config.recursive = depth == "Recursiva"
            elif action == "3":
                kind = choose("Elementos", list(ElementKind))
                if kind is not None:
                    config.kind = kind
            elif action == "4":
                representation = choose("Representación", list(Representation))
                if representation is not None:
                    config.representation = representation
            elif action == "5":
                if config.root is None:
                    write("Selecciona primero un directorio.")
                elif yes("¿Iniciar generación de TXT y Excel con estas opciones?"):
                    write("Explorando y preparando archivos temporales. Ctrl+C cancela.")
                    result = generate(
                        config,
                        overwrite,
                        lambda: yes("Preparación terminada. ¿Guardar los resultados?"),
                    )
                    write(summary(result))
            elif action == "6":
                write(
                    summary(config.last_result)
                    if config.last_result
                    else "Todavía no hay resultados."
                )
            else:
                write("Opción no válida.")
        except KeyboardInterrupt:
            write("\nOperación cancelada. Puedes continuar o elegir 0 para salir.")
        except EOFError:
            write("\nFin de entrada. Saliendo.")
            return 0
        except Cancelled as error:
            write(str(error) or "Operación cancelada.")
        except (OSError, ValueError) as error:
            write(f"No se pudo completar la operación: {error}")


def main() -> int:
    """Entrada de consola; --version y --help funcionan sin abrir el menú."""
    parser = argparse.ArgumentParser(description="FolderLister: listados locales TXT y Excel.")
    parser.add_argument("--version", action="version", version=f"FolderLister {__version__}")
    parser.parse_args()
    # Mantiene conectores y acentos en consolas y redirecciones de Windows.
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    return run_menu()
