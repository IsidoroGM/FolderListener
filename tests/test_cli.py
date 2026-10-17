"""Diálogos, configuración persistente y fallback gráfico."""

from folderlister.cli import run_menu
from folderlister.config import Session
from folderlister.models import ElementKind, Representation
from folderlister.selection import browse_directory


def test_menu_config_and_generation(tmp_path):
    answers = iter(
        ["invalid", "1", "1", str(tmp_path), "2", "2", "3", "2", "4", "4", "5", "s", "s", "6", "0"]
    )
    messages = []
    session = Session()
    assert run_menu(session, lambda prompt: next(answers), messages.append) == 0
    assert session.root == tmp_path and session.recursive
    assert session.kind == ElementKind.FILES
    assert session.representation == Representation.TREE
    assert session.last_result is not None
    assert any("Opción no válida" in message for message in messages)


def test_graphical_fallback(tmp_path, monkeypatch):
    import folderlister.cli as cli

    def unavailable():
        raise RuntimeError("Sin tkinter")

    monkeypatch.setattr(cli, "graphical_directory", unavailable)
    answers = iter(["1", "3", str(tmp_path), "0"])
    session = Session()
    messages = []
    run_menu(session, lambda prompt: next(answers), messages.append)
    assert session.root == tmp_path
    assert any("consola" in message for message in messages)


def test_navigation(tree):
    answers = iter(["invalid", "1", "e"])
    assert browse_directory(tree, lambda prompt: next(answers), lambda text: None) == tree / "beta"


def test_interrupt_then_eof():
    count = 0
    messages = []

    def read(prompt):
        nonlocal count
        count += 1
        if count == 1:
            raise KeyboardInterrupt()
        raise EOFError()

    assert run_menu(read=read, write=messages.append) == 0
    assert any("cancelada" in message for message in messages)
