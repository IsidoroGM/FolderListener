"""Construye un portátil nativo con avisos y manifiesto verificable."""

import hashlib
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Recopila licencias, ejecuta PyInstaller y escribe manifiesto SHA-256."""
    subprocess.run([sys.executable, str(ROOT / "scripts" / "licenses.py")], check=True, cwd=ROOT)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            str(ROOT / "packaging" / "folderlister.spec"),
        ],
        check=True,
        cwd=ROOT,
    )
    binary = ROOT / "dist" / ("FolderLister.exe" if sys.platform == "win32" else "FolderLister")
    subprocess.run([str(binary), "--version"], check=True)
    with binary.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    manifest = {
        "application": "FolderLister",
        "version": "1.0.0",
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "python": sys.version,
        "libc": platform.libc_ver(),
        "signed": False,
        "sha256": digest,
    }
    (ROOT / "dist" / "build-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    for name in ("README.md", "LICENSE.template"):
        shutil.copy2(ROOT / name, ROOT / "dist" / name)


if __name__ == "__main__":
    main()
