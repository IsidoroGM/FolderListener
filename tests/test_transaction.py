"""Conservación de resultados y limpieza ante errores y cancelaciones."""

import pytest

from folderlister.config import Session
from folderlister.controller import generate
from folderlister.models import Cancelled
from folderlister.rendering import output_paths


def old_outputs(root):
    paths = output_paths(root)
    for path in paths:
        path.write_bytes(b"previous output")
    return paths


def assert_untouched(root, paths):
    assert all(path.read_bytes() == b"previous output" for path in paths)
    assert not list(root.glob(".folderlister-*"))


def test_rejected_overwrite(tmp_path):
    paths = old_outputs(tmp_path)
    with pytest.raises(Cancelled):
        generate(Session(root=tmp_path))
    assert_untouched(tmp_path, paths)


def test_accepted_overwrite_excludes_outputs(tmp_path):
    paths = old_outputs(tmp_path)
    seen = []

    def confirm(existing):
        seen.extend(existing)
        return True

    result = generate(Session(root=tmp_path, recursive=True), confirm)
    assert set(seen) == set(paths)
    assert result.statistics.files_listed == 0
    assert result.statistics.directories_listed == 0
    assert paths[2].read_bytes() == b"previous output"  # Log histórico conservado.


def test_cancel_before_publish(tmp_path):
    paths = old_outputs(tmp_path)
    with pytest.raises(Cancelled):
        generate(Session(root=tmp_path), lambda paths: True, lambda: False)
    assert_untouched(tmp_path, paths)


def test_export_failure_preserves_old(tmp_path, monkeypatch):
    from folderlister.export_xlsx import XlsxExporter

    paths = old_outputs(tmp_path)

    def fail(*args):
        raise OSError("disco lleno simulado")

    monkeypatch.setattr(XlsxExporter, "finish", fail)
    with pytest.raises(OSError, match="disco lleno"):
        generate(Session(root=tmp_path), lambda paths: True)
    assert_untouched(tmp_path, paths)


def test_publish_failure_rolls_back(tmp_path, monkeypatch):
    import folderlister.transaction as transaction

    paths = old_outputs(tmp_path)
    original = transaction.os.replace

    def fail_once(source, target):
        if source.name == paths[1].name and source.parent != tmp_path:
            raise OSError("fallo de sustitución")
        return original(source, target)

    monkeypatch.setattr(transaction.os, "replace", fail_once)
    with pytest.raises(OSError, match="sustitución"):
        generate(Session(root=tmp_path), lambda paths: True)
    assert_untouched(tmp_path, paths)


def test_concurrent_output_creation_not_overwritten(tmp_path):
    path = output_paths(tmp_path)[0]

    def confirm():
        path.write_bytes(b"concurrent output")
        return True

    with pytest.raises(OSError, match="cambió"):
        generate(Session(root=tmp_path), confirm_publish=confirm)
    assert path.read_bytes() == b"concurrent output"
    assert not list(tmp_path.glob(".folderlister-*"))


def test_write_probe_before_scan(tmp_path, monkeypatch):
    import folderlister.controller as controller
    import folderlister.transaction as transaction

    def denied(*args, **kwargs):
        raise PermissionError("sin escritura")

    def never(*args, **kwargs):
        pytest.fail("No debe explorar sin poder escribir")

    monkeypatch.setattr(transaction.tempfile, "TemporaryDirectory", denied)
    monkeypatch.setattr(controller, "scan", never)
    with pytest.raises(PermissionError):
        generate(Session(root=tmp_path))


def test_keyboard_interrupt_cleans(tmp_path, monkeypatch):
    import folderlister.controller as controller

    paths = old_outputs(tmp_path)

    def interrupted(*args, **kwargs):
        raise KeyboardInterrupt()

    monkeypatch.setattr(controller, "scan", interrupted)
    with pytest.raises(KeyboardInterrupt):
        generate(Session(root=tmp_path), lambda paths: True)
    assert_untouched(tmp_path, paths)


def test_partial_result_publishes_log_and_consistent_summary(tree, monkeypatch):
    from openpyxl import load_workbook

    import folderlister.scanner as scanner

    original = scanner.directory_handle

    def denied(path):
        if path.name == "beta":
            raise PermissionError("permiso denegado de prueba")
        return original(path)

    monkeypatch.setattr(scanner, "directory_handle", denied)
    result = generate(Session(root=tree, recursive=True))
    assert result.partial and result.statistics.issues == 1
    assert len(result.outputs) == 3
    assert "beta" in result.outputs[2].read_text(encoding="utf-8")
    book = load_workbook(result.outputs[1], read_only=True)
    values = dict(list(book["Resumen"].values)[1:])
    assert values["Número de errores / advertencias"] == 1
    book.close()


def test_openpyxl_tempfiles_removed_on_abort(tmp_path, monkeypatch):
    from openpyxl.worksheet._writer import ALL_TEMP_FILES

    from folderlister.export_xlsx import XlsxExporter

    before = set(ALL_TEMP_FILES)

    def fail(*args):
        raise OSError("abortar")

    monkeypatch.setattr(XlsxExporter, "finish", fail)
    with pytest.raises(OSError):
        generate(Session(root=tmp_path))
    assert set(ALL_TEMP_FILES) == before
