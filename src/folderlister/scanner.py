"""Exploración DFS iterativa con orden por nivel y emisión incremental."""

import os
import stat
from collections.abc import Callable, Iterator
from pathlib import Path

from folderlister.config import Session
from folderlister.filesystem import directory_handle, directory_identity
from folderlister.filters import excluded
from folderlister.issues import IssueLog
from folderlister.models import Cancelled, ElementKind, Entry, Representation, Statistics


def scan(
    root: Path,
    config: Session,
    statistics: Statistics,
    issues: IssueLog,
    excluded_paths: set[Path],
    cancelled: Callable[[], bool] = lambda: False,
) -> Iterator[Entry]:
    """Emite elementos y contexto visual; no lee contenidos ni sigue enlaces."""
    active: set[tuple[int, int]] = set()

    def level(directory: Path, branches: tuple[bool, ...]) -> Iterator[Entry]:
        identity: tuple[int, int] | None = None

        def register(value: tuple[int, int]) -> None:
            nonlocal identity
            identity = value

        try:
            # El generador conserva esta identidad mientras se recorre su descendencia.
            yield from read_level(directory, branches, register)
        finally:
            if identity is not None:
                active.discard(identity)

    def read_level(
        directory: Path, branches: tuple[bool, ...], register: Callable[[tuple[int, int]], None]
    ) -> Iterator[Entry]:
        items: list[tuple[str, bool]] = []
        try:
            with directory_handle(directory) as handle, os.scandir(handle) as children:
                identity = directory_identity(handle)
                if identity[1] and identity in active:
                    issues.record(directory, "evitar ciclo", "Directorio ya presente en esta rama")
                    return
                if identity[1]:
                    active.add(identity)
                    register(identity)
                statistics.directories_scanned += 1
                for child in children:
                    if cancelled():
                        raise Cancelled()
                    path = directory / child.name
                    if path in excluded_paths:
                        continue
                    try:
                        info = child.stat(follow_symlinks=False)
                        if excluded(child.name, info):
                            continue
                        is_directory = stat.S_ISDIR(info.st_mode)
                        if not is_directory and config.kind == ElementKind.DIRECTORIES:
                            continue
                        items.append((child.name, is_directory))
                    except OSError as error:
                        issues.record(path, "leer atributos", error)
        except OSError as error:
            issues.record(directory, "explorar directorio", error)
        items.sort(key=lambda item: (not item[1], item[0].casefold(), item[0]))
        for index, (name, is_directory) in enumerate(items):
            path = directory / name
            included = not (is_directory and config.kind == ElementKind.FILES)
            yield Entry(
                path,
                path.relative_to(root),
                is_directory,
                included,
                branches + (index == len(items) - 1,),
            )

    stack = [level(root, ())]
    while stack:
        if cancelled():
            raise Cancelled()
        entry = next(stack[-1], None)
        if entry is None:
            stack.pop()
            continue
        if entry.included:
            if entry.is_directory:
                statistics.directories_listed += 1
            else:
                statistics.files_listed += 1
        if entry.included or config.representation == Representation.TREE:
            yield entry
        if entry.is_directory and config.recursive:
            stack.append(level(entry.path, entry.branches))
