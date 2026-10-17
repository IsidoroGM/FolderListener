param([string]$Python = '.\.venv\Scripts\python.exe')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
$projectPath = (Get-Location).Path
$installedKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\{4083FC7B-04CD-4A51-9D30-A56B828C1E64}_is1'
if (Test-Path -LiteralPath $installedKey) {
    throw 'Ya existe una instalación de FolderLister; la prueba no la modifica.'
}
$installPath = [IO.Path]::GetFullPath((Join-Path $projectPath 'build\installer-smoke'))
if (-not $installPath.StartsWith($projectPath + [IO.Path]::DirectorySeparatorChar)) {
    throw 'El destino de prueba debe estar dentro del proyecto.'
}
if (Test-Path -LiteralPath $installPath) { throw 'El destino de prueba ya existe; no se modifica.' }
$setupPath = Join-Path $projectPath 'dist\FolderLister-1.0.0-setup.exe'
$logPath = Join-Path $projectPath 'build\installer-smoke.log'
$arguments = @('/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/SP-', '/NOICONS',
    '/TASKS=', '/CURRENTUSER', ('/DIR="' + $installPath + '"'), ('/LOG="' + $logPath + '"'))
$setup = Start-Process -FilePath $setupPath -ArgumentList $arguments -WindowStyle Hidden -Wait -PassThru
if ($setup.ExitCode -ne 0) { throw "Instalador: código $($setup.ExitCode)" }
try {
    & $Python scripts/smoke.py (Join-Path $installPath 'FolderLister.exe')
    if ($LASTEXITCODE -ne 0) { throw 'Falló el ejecutable instalado.' }
} finally {
    $uninstall = Join-Path $installPath 'unins000.exe'
    if (Test-Path -LiteralPath $uninstall) {
        $process = Start-Process -FilePath $uninstall -ArgumentList '/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART' -WindowStyle Hidden -Wait -PassThru
        if ($process.ExitCode -ne 0) { throw "Desinstalador: código $($process.ExitCode)" }
    }
}
if (Test-Path -LiteralPath (Join-Path $installPath 'FolderLister.exe')) {
    throw 'La desinstalación dejó el ejecutable.'
}
if (Test-Path -LiteralPath $installedKey) { throw 'Quedó el registro de desinstalación.' }
Write-Output 'Instalación, generación y desinstalación: correctas.'
