# Construir con python scripts/build.py desde la plataforma objetivo.
import os
from pathlib import Path

root = Path(SPECPATH).parent
analysis = Analysis(
    [str(root / "scripts" / "entrypoint.py")],
    pathex=[str(root / "src")],
    datas=[(str(root / "dist" / "THIRD_PARTY_NOTICES"), "THIRD_PARTY_NOTICES")],
    hiddenimports=[],
    hookspath=[],
    excludes=["pytest", "ruff"],
    noarchive=False,
)
archive = PYZ(analysis.pure)
executable = EXE(
    archive, analysis.scripts, analysis.binaries, analysis.datas,
    name="FolderLister", debug=False, strip=False, upx=False, console=True,
    codesign_identity=os.environ.get("SIGN_IDENTITY"),
)
