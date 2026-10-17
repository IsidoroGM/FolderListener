param([string]$Python = '.\.venv\Scripts\python.exe', [switch]$Installer)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
& $Python scripts/build.py
if ($LASTEXITCODE -ne 0) { throw 'Falló PyInstaller' }
& $Python scripts/smoke.py dist/FolderLister.exe
if ($LASTEXITCODE -ne 0) { throw 'Falló la prueba del ejecutable' }
if ($Installer) {
    $compiler = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    $compilerPath = if ($null -ne $compiler) { $compiler.Source } else { '.\.tools\inno\ISCC.exe' }
    if (-not (Test-Path -LiteralPath $compilerPath)) {
        throw 'Instala Inno Setup 6 y añade ISCC.exe a PATH o usa .tools\inno.'
    }
    & $compilerPath packaging/windows/installer.iss
    if ($LASTEXITCODE -ne 0) { throw 'Falló Inno Setup' }
}
