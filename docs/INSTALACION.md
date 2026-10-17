# Instalación y desinstalación

## Portátil

Descomprime el archivo de tu sistema y arquitectura manteniendo juntos el ejecutable
y los avisos de licencia. Ejecuta `FolderLister.exe` en Windows; en macOS/Linux abre
una terminal y ejecuta `./FolderLister`. No necesita Python ni conexión. El menú está
en español; `--help` y `--version` permiten comprobar la instalación.

Windows x64, Linux x86-64 y macOS Intel/Apple Silicon requieren compilaciones nativas
independientes. No intercambiar ejecutables entre plataformas o arquitecturas.

En Linux la compatibilidad depende de la glibc del sistema de compilación. En macOS
el despliegue mínimo depende del intérprete y SDK usados. Registrar ambos en cada
entrega; el flujo propuesto no garantiza compatibilidad con sistemas antiguos.

## Instaladores

- Windows: ejecutar `FolderLister-1.0.0-setup.exe`. Instalación por usuario, sin elevación,
  acceso directo en Inicio y escritorio opcional. Desinstalar desde Aplicaciones.
- macOS: `sudo installer -pkg FolderLister-1.0.0-<arquitectura>.pkg -target /`.
  Ejecutar `/usr/local/bin/folderlister` desde Terminal. El instalador necesita permisos
  para `/usr/local`; el programa no necesita ejecutarse como administrador.
- Debian/Ubuntu: `sudo apt install ./folderlister_1.0.0_amd64.deb`.
  Ejecutar `folderlister`. Desinstalar con `sudo apt remove folderlister`.

En macOS no existe un desinstalador universal de pkg: eliminar únicamente el enlace
`/usr/local/bin/folderlister` y el directorio de aplicación
`/usr/local/lib/folderlister`, y ejecutar `sudo pkgutil --forget local.folderlister.cli`.
Comprobar antes que esas rutas pertenecen al paquete instalado. Los inventarios
generados permanecen en sus carpetas y no se eliminan al desinstalar.

Portátil: elimina la carpeta donde descomprimiste el programa. Desde código:
`python -m pip uninstall folderlister`, o elimina el entorno virtual propio.

## Entorno de desarrollo

Usar Python 3.12, un entorno virtual y Visual Studio Code con la extensión oficial
de Python. Seleccionar `.venv` como intérprete. `requirements-build.txt` fija también
dependencias transitivas de las herramientas de compilación. Instalar con:

```sh
python -m pip install -r requirements-build.txt
python -m pip install --no-build-isolation --no-deps -e .
```

Tkinter puede faltar en instalaciones mínimas de Python. La consola seguirá operativa.
En Linux puede instalarse el paquete `python3-tk` de la distribución para habilitarlo.
