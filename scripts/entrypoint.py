"""Entrada absoluta para PyInstaller, sin importaciones relativas."""

from folderlister.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
