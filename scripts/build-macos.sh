#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-.venv/bin/python}"
"$PYTHON" scripts/build.py
"$PYTHON" scripts/smoke.py dist/FolderLister
stage="$(mktemp -d)"
trap 'rm -rf -- "$stage"' EXIT
mkdir -p "$stage/usr/local/lib/folderlister" "$stage/usr/local/bin"
cp dist/FolderLister "$stage/usr/local/lib/folderlister/FolderLister"
cp -R dist/THIRD_PARTY_NOTICES "$stage/usr/local/lib/folderlister/"
cp LICENSE.template "$stage/usr/local/lib/folderlister/"
ln -s ../lib/folderlister/FolderLister "$stage/usr/local/bin/folderlister"
if [ -n "${SIGN_IDENTITY:-}" ]; then
    codesign --force --options runtime --timestamp --sign "$SIGN_IDENTITY" "$stage/usr/local/lib/folderlister/FolderLister"
    codesign --verify --strict --verbose=2 "$stage/usr/local/lib/folderlister/FolderLister"
fi
pkgbuild --root "$stage" --identifier local.folderlister.cli --version 1.0.0 \
    --install-location / "dist/FolderLister-1.0.0-$(uname -m).pkg"
