#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-.venv/bin/python}"
"$PYTHON" scripts/build.py
"$PYTHON" scripts/smoke.py dist/FolderLister
test "$(uname -m)" = x86_64
stage="$(mktemp -d)"
trap 'rm -rf -- "$stage"' EXIT
mkdir -p "$stage/DEBIAN" "$stage/usr/lib/folderlister" "$stage/usr/bin" "$stage/usr/share/doc/folderlister"
install -m 755 dist/FolderLister "$stage/usr/lib/folderlister/FolderLister"
ln -s ../lib/folderlister/FolderLister "$stage/usr/bin/folderlister"
cp -R dist/THIRD_PARTY_NOTICES "$stage/usr/share/doc/folderlister/"
cp README.md LICENSE.template "$stage/usr/share/doc/folderlister/"
cat > "$stage/DEBIAN/control" <<'CONTROL'
Package: folderlister
Version: 1.0.0
Section: utils
Priority: optional
Architecture: amd64
Maintainer: FolderLister release team
Depends: libc6 (>= 2.35), zlib1g
Description: Inventario local de carpetas y archivos en TXT y XLSX
 Aplicacion de consola en espanol, sin servicios externos.
CONTROL
dpkg-deb --root-owner-group --build "$stage" dist/folderlister_1.0.0_amd64.deb
