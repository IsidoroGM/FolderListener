# Compilación y distribución nativa

Preparar Python 3.12.11 y un entorno virtual en cada sistema. Instalar
`requirements-build.txt` y el proyecto con `--no-build-isolation --no-deps`.
Ejecutar pytest, Ruff y formato antes de construir. Las versiones de paquetes están
fijadas; conservar el manifiesto del sistema, wheels y SHA-256 para cada entrega.
Esto reproduce el procedimiento y las entradas, no garantiza binarios idénticos
bit a bit: firmas, fechas ZIP y herramientas nativas pueden variar.

## Windows x64

```powershell
powershell -File scripts/build-windows.ps1
# Con Inno Setup 6.7.3 disponible en PATH:
powershell -File scripts/build-windows.ps1 -Installer
```

También se puede ejecutar `ISCC.exe packaging/windows/installer.iss` tras construir
el portátil. Salidas en `dist/`: `FolderLister.exe` y
`FolderLister-1.0.0-setup.exe`. Inno Setup se puede instalar en modo portátil local
con sus opciones `/PORTABLE=1 /DIR=...`; verificar la firma del instalador del compilador.

Para firma Authenticode usar un certificado del editor y `signtool` del Windows SDK:

```powershell
signtool sign /sha1 CERTIFICATE_THUMBPRINT /fd SHA256 /tr TIMESTAMP_URL /td SHA256 dist/FolderLister.exe
signtool verify /pa /v dist/FolderLister.exe
```

Firmar el ejecutable antes de incluirlo en Inno Setup. Para una entrega firmada completa,
configurar `SignTool` y `SignedUninstaller=yes` en el script de Inno y firmar/verificar
también el instalador. No hay certificados ni secretos en este proyecto. Los artefactos
generados por defecto están sin firmar y pueden mostrar avisos de SmartScreen.

## macOS Intel y Apple Silicon

```sh
bash scripts/build-macos.sh
```

Ejecutar en cada arquitectura con Python nativo correspondiente. Produce un portátil
de terminal y `FolderLister-1.0.0-<arquitectura>.pkg`. La selección gráfica es opcional.
El script acepta `SIGN_IDENTITY` para firmar el ejecutable con Developer ID Application.
El spec transmite esa identidad a PyInstaller mediante `codesign_identity` para
firmar también las bibliotecas embebidas al preparar una entrega notarizada.
Comprobar las dependencias incluidas y entitlements necesarios para la versión de Python.

Firmar el pkg con Developer ID Installer en un nombre distinto y notarizar:

```sh
productsign --sign "Developer ID Installer: TITULAR (TEAMID)" unsigned.pkg signed.pkg
xcrun notarytool submit signed.pkg --keychain-profile PERFIL --wait
xcrun stapler staple signed.pkg
pkgutil --check-signature signed.pkg
spctl --assess --type install --verbose signed.pkg
```

El perfil debe configurarse en el llavero del equipo de firma; no guardar contraseñas
en scripts. Comprobar el paquete en una máquina limpia y la descarga real con cuarentena.
Una firma ad hoc del proceso de compilación no equivale a Developer ID ni notarización.

## Debian/Ubuntu x86-64

```sh
bash scripts/build-linux.sh
```

Requiere `dpkg-deb`. El script está orientado a Ubuntu 22.04 (glibc 2.35) o equivalentes
compatibles. Si se compila en una distribución más nueva, verificar símbolos y actualizar
la dependencia mínima de libc; no distribuir el paquete con un mínimo inferior al real.
PyInstaller no incluye glibc. Probar también ausencia de entorno gráfico y montaje noexec
del directorio temporal (puede impedir arrancar un ejecutable onefile).
Usar `dpkg-deb --info` y `dpkg-deb --contents` para revisar el paquete. Para repositorios
APT, firmar el repositorio con las herramientas nativas; un .deb no está firmado por defecto.

## CI y publicación

`.github/workflows/verify.yml` prepara trabajos independientes para Windows, Linux,
macOS Intel y ARM. Los runners y las acciones son entradas externas; fijar sus revisiones
de imagen/commit si se requiere una cadena de suministro estrictamente reproducible.
Consultar [las imágenes oficiales](https://github.com/actions/runner-images) antes de
activar el flujo. El flujo no se ha ejecutado por el mero hecho de crear este archivo.

`scripts/smoke.py` ejecuta el menú del binario, genera y reabre TXT/XLSX y verifica el
rechazo de sobrescritura. Complementarlo con `VERIFICACION_MANUAL.md`: el smoke test
no valida un instalador ni Gatekeeper/SmartScreen ni equipos sin Python instalado.

`scripts/licenses.py` recoge avisos de las distribuciones instaladas y de Python/Tcl/Tk
cuando están disponibles. `scripts/build.py` los incorpora, verifica `--version` y genera
un manifiesto con plataforma, arquitectura, Python y SHA-256. Auditar también las DLL,
dylib y bibliotecas del sistema realmente incluidas por PyInstaller antes de publicar.
Conservar los avisos junto al portátil aunque también estén embebidos.

Referencias: [PyInstaller](https://pyinstaller.org/en/stable/usage.html),
[Inno Setup](https://jrsoftware.org/isdl.php),
[notarización Apple](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution).
