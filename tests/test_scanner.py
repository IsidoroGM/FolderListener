"""Exploración, filtros, errores recuperables y límites de memoria."""

import os
import stat
from pathlib import Path
from types import SimpleNamespace

import pytest

from folderlister.config import Session
from folderlister.filters import excluded
from folderlister.issues import IssueLog
from folderlister.models import Cancelled, ElementKind, Representation, Statistics
from folderlister.scanner import scan
from folderlister.selection import validate_directory


def collect(root, **options):
    stats = Statistics()
    log = IssueLog(root / ".test.log", stats)
    try:
        entries = list(scan(root, Session(root=root, **options), stats, log, set()))
        return entries, stats
    finally:
        log.close()


def test_empty(tmp_path):
    entries, stats = collect(tmp_path)
    assert entries == []
    assert stats.directories_scanned == 1


def test_first_level_and_unicode(tree):
    entries, stats = collect(tree)
    assert [entry.path.name for entry in entries] == [
        "beta",
        "Árbol",
        "A con espacios.txt",
        "z.txt",
    ]
    assert all(entry.depth == 1 for entry in entries)
    assert (stats.directories_listed, stats.files_listed) == (2, 2)


@pytest.mark.parametrize("kind", list(ElementKind))
def test_recursive_types_and_hierarchy(tree, kind):
    entries, stats = collect(tree, recursive=True, kind=kind)
    expected = ["beta", "sub", "profundo.txt", "Z.txt", "Árbol", "A con espacios.txt", "z.txt"]
    if kind == ElementKind.FILES:
        expected = [name for name in expected if name.endswith(".txt")]
    if kind == ElementKind.DIRECTORIES:
        expected = [name for name in expected if not name.endswith(".txt")]
    assert [entry.path.name for entry in entries] == expected
    assert stats.directories_scanned == 4


def test_context_not_counted(tree):
    entries, stats = collect(
        tree, recursive=True, kind=ElementKind.FILES, representation=Representation.TREE
    )
    assert all(not entry.included for entry in entries if entry.is_directory)
    assert stats.directories_listed == 0
    assert stats.files_listed == 4


@pytest.mark.parametrize(
    "name,attributes,flags,mode",
    [
        (".hidden", 0, 0, stat.S_IFDIR),
        ("hidden", 2, 0, stat.S_IFREG),
        ("system", 4, 0, stat.S_IFDIR),
        ("junction", 0x400, 0, stat.S_IFDIR),
        ("mac", 0, 0x8000, stat.S_IFREG),
        ("link", 0, 0, stat.S_IFLNK),
        ("pipe", 0, 0, stat.S_IFIFO),
    ],
)
def test_native_hidden_and_special(name, attributes, flags, mode):
    info = SimpleNamespace(st_mode=mode, st_file_attributes=attributes, st_flags=flags)
    assert excluded(name, info)


def test_invalid_directory(tmp_path):
    with pytest.raises(ValueError):
        validate_directory("relative")
    with pytest.raises(OSError):
        validate_directory(tmp_path / "missing")
    file = tmp_path / "file"
    file.touch()
    with pytest.raises(OSError):
        validate_directory(file)


def test_symlink_cycle_and_external(tree, tmp_path):
    external = tmp_path / "external"
    external.mkdir()
    (external / "never.txt").touch()
    try:
        (tree / "cycle").symlink_to(tree, target_is_directory=True)
        (tree / "external").symlink_to(external, target_is_directory=True)
    except OSError:
        pytest.skip("El sistema no permite crear symlinks sin privilegios.")
    entries, _ = collect(tree, recursive=True)
    assert not {"cycle", "external", "never.txt"} & {entry.path.name for entry in entries}
    with pytest.raises(OSError):
        validate_directory(tree / "external")


def test_unreadable_continues(tree, monkeypatch):
    import folderlister.scanner as scanner

    original = scanner.directory_handle

    def denied(path):
        if path.name == "beta":
            raise PermissionError("simulado")
        return original(path)

    monkeypatch.setattr(scanner, "directory_handle", denied)
    entries, stats = collect(tree, recursive=True)
    assert stats.issues == 1
    assert entries[-1].path.name == "z.txt"
    assert "explorar directorio" in (tree / ".test.log").read_text(encoding="utf-8")


def test_cancelled(tree):
    stats = Statistics()
    log = IssueLog(tree / ".log", stats)
    with pytest.raises(Cancelled):
        list(scan(tree, Session(root=tree), stats, log, set(), lambda: True))


def test_scandir_closed_before_yield(tree, monkeypatch):
    import folderlister.scanner as scanner

    original = os.scandir
    opened = 0

    class Tracked:
        def __init__(self, path):
            self.iterator = original(path)

        def __enter__(self):
            nonlocal opened
            opened += 1
            return self.iterator

        def __exit__(self, *args):
            nonlocal opened
            self.iterator.close()
            opened -= 1

    monkeypatch.setattr(scanner.os, "scandir", Tracked)
    stats = Statistics()
    log = IssueLog(tree / ".log", stats)
    iterator = scan(tree, Session(root=tree, recursive=True), stats, log, set())
    next(iterator)
    assert opened == 0
    assert stats.directories_scanned == 1  # No se ha leído aún el subárbol.
    iterator.close()


def test_network_style_validation_simulated(monkeypatch):
    from contextlib import nullcontext

    import folderlister.selection as selection

    if os.name != "nt":
        pytest.skip("Semántica UNC exclusiva de Windows; CI Windows cubre este caso.")
    root = Path(r"\\servidor\recurso\carpeta")
    visited = []

    def handle(path):
        visited.append(path)
        return nullcontext(path)

    monkeypatch.setattr(selection, "directory_handle", handle)
    monkeypatch.setattr(selection.os, "scandir", lambda path: nullcontext(iter(())))
    assert validate_directory(root) == root
    assert visited == [root]


def test_iterative_depth_over_python_recursion_limit(tmp_path, monkeypatch):
    from contextlib import nullcontext

    import folderlister.scanner as scanner

    depth = 1100
    root_parts = len(tmp_path.parts)

    class Child:
        name = "d"

        def stat(self, *, follow_symlinks):
            assert not follow_symlinks
            return SimpleNamespace(st_mode=stat.S_IFDIR)

    def children(path):
        level = len(path.parts) - root_parts
        return nullcontext(iter([Child()] if level < depth else []))

    monkeypatch.setattr(scanner, "directory_handle", lambda path: nullcontext(path))
    monkeypatch.setattr(scanner, "directory_identity", lambda path: (1, len(path.parts)))
    monkeypatch.setattr(scanner.os, "scandir", children)
    entries, stats = collect(tmp_path, recursive=True)
    assert len(entries) == depth
    assert entries[-1].depth == depth
    assert stats.directories_scanned == depth + 1


@pytest.mark.skipif(os.name != "nt", reason="Prueba nativa de atributos Windows")
def test_real_windows_hidden_and_junction(tree, tmp_path):
    import ctypes
    import subprocess

    hidden = tree / "oculto_nativo.txt"
    hidden.touch()
    setter = ctypes.windll.kernel32.SetFileAttributesW
    assert setter(str(hidden), 2)
    outside = tmp_path / "fuera"
    outside.mkdir()
    (outside / "no_entrar.txt").touch()
    junction = tree / "union"
    process = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(outside)],
        capture_output=True,
        check=False,
    )
    assert process.returncode == 0, process.stderr
    try:
        entries, _ = collect(tree, recursive=True)
        assert not {"oculto_nativo.txt", "union", "no_entrar.txt"} & {
            entry.path.name for entry in entries
        }
        with pytest.raises(OSError):
            validate_directory(junction)
    finally:
        setter(str(hidden), 0x80)
        junction.rmdir()


def test_disappeared_entry_logged_and_other_entries_survive(tmp_path, monkeypatch):
    from contextlib import nullcontext

    import folderlister.scanner as scanner

    class Child:
        def __init__(self, name):
            self.name = name

        def stat(self, *, follow_symlinks):
            if self.name == "gone":
                raise FileNotFoundError("desaparecido durante lectura")
            return SimpleNamespace(st_mode=stat.S_IFREG)

    monkeypatch.setattr(scanner, "directory_handle", lambda path: nullcontext(path))
    monkeypatch.setattr(
        scanner.os,
        "scandir",
        lambda path: nullcontext(iter([Child("gone"), Child("z"), Child("a"), Child("A")])),
    )
    entries, stats = collect(tmp_path)
    assert [entry.path.name for entry in entries] == ["A", "a", "z"]
    assert stats.issues == 1


def test_physical_cycle_is_stopped(tree, monkeypatch):
    import folderlister.scanner as scanner

    # Un montaje cíclico devuelve la misma identidad física que la raíz.
    monkeypatch.setattr(scanner, "directory_identity", lambda handle: (1, 100))
    entries, stats = collect(tree, recursive=True)
    assert [entry.path.name for entry in entries] == [
        "beta",
        "Árbol",
        "A con espacios.txt",
        "z.txt",
    ]
    assert stats.directories_scanned == 1
    assert stats.issues == 2
