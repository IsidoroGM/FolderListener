"""Orquestación de una generación completa con recursos acotados."""

from collections.abc import Callable
from contextlib import ExitStack
from datetime import datetime
from pathlib import Path
from time import perf_counter

from folderlister.config import Session
from folderlister.export_txt import TxtExporter
from folderlister.export_xlsx import XlsxExporter
from folderlister.filesystem import directory_handle
from folderlister.issues import IssueLog
from folderlister.models import Cancelled, Result, Statistics
from folderlister.rendering import output_paths
from folderlister.scanner import scan
from folderlister.selection import validate_directory
from folderlister.transaction import OutputTransaction


def generate(
    config: Session,
    confirm_overwrite: Callable[[tuple[Path, ...]], bool] = lambda paths: False,
    confirm_publish: Callable[[], bool] = lambda: True,
    cancelled: Callable[[], bool] = lambda: False,
    max_rows: int = 1_048_576,
) -> Result:
    """Genera ambas salidas; no autoriza sobrescrituras por defecto.

    confirm_publish permite cancelar después de explorar, antes de tocar salidas.
    Los temporales sirven además de prueba de escritura previa al escaneo.
    """
    if config.root is None:
        raise ValueError("Selecciona primero un directorio.")
    root = validate_directory(config.root)
    started = datetime.now().astimezone()
    timer = perf_counter()
    stats = Statistics()
    outputs = output_paths(root)
    with ExitStack() as resources:
        resources.enter_context(directory_handle(root))
        transaction = OutputTransaction(outputs, confirm_overwrite)
        resources.callback(transaction.close)
        issues = IssueLog(transaction.stage(outputs[2]), stats)
        resources.callback(issues.close)
        txt = TxtExporter(transaction.stage(outputs[0]), root, config, started)
        resources.callback(txt.close)
        xlsx = XlsxExporter(transaction.stage(outputs[1]), issues, txt.preserve, max_rows)
        resources.callback(xlsx.close)
        for entry in scan(
            root, config, stats, issues, set(outputs) | {transaction.work}, cancelled
        ):
            txt.append(entry)
            xlsx.append(entry, config)
        stats.duration = perf_counter() - timer
        xlsx.finish(root, config, started, stats)
        txt.finish(stats)
        txt.close()
        issues.close()
        published = outputs if stats.issues else outputs[:2]
        if cancelled() or not confirm_publish():
            raise Cancelled("Publicación cancelada; salidas anteriores conservadas.")
        transaction.publish(published)
    result = Result(root, started, stats, published)
    config.last_result = result
    return result
