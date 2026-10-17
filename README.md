# FolderLister

Herramienta de consola en español que lista los archivos y carpetas de un directorio
y exporta el resultado a **TXT y Excel**. Útil para documentar la estructura de un
proyecto o crear un inventario de archivos sin abrir su contenido.

## Qué permite hacer

- Explorar solo el primer nivel o incluir todas las subcarpetas.
- Listar archivos, carpetas o ambos.
- Mostrar nombres, rutas absolutas, rutas relativas o una estructura de árbol.
- Elegir la carpeta por ruta, navegación en consola o selector gráfico opcional.

Funciona sin conexión durante su uso y no envía datos. Excluye elementos ocultos,
archivos de sistema de Windows y enlaces simbólicos; consulta las
[restricciones de exploración](docs/USO.md).

## Inicio rápido

Necesitas **Python 3.12 o posterior**. Desde la carpeta del proyecto, en Windows:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m folderlister
```

En Linux/macOS:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m folderlister
```

La instalación descarga las dependencias. Si ya tienes una versión portátil,
ejecuta `FolderLister.exe` en Windows o `./FolderLister` en Linux/macOS, sin instalar Python.

## Uso

1. Selecciona el directorio que quieres inventariar.
2. Configura la profundidad, los elementos y el formato desde el menú.
3. Elige **Generar listado** y confirma el inicio y el guardado de los resultados.

Por ejemplo, al seleccionar una carpeta llamada `Proyectos`, se guardan dentro de ella:

| Archivo | Contenido |
| --- | --- |
| `Proyectos_listado.txt` | Listado de texto con cabecera y resumen. |
| `Proyectos_listado.xlsx` | Libro Excel con hojas de resumen y elementos. |
| `Proyectos_errores.log` | Registro de incidencias, solo si se producen. |

Si ya existen salidas, se pide confirmación antes de sobrescribirlas.
`Ctrl+C` cancela la operación actual y `0` en el menú principal cierra la aplicación.

## Desarrollo

Para instalar las herramientas de desarrollo y ejecutar las comprobaciones en Windows:

```powershell
.\.venv\Scripts\python.exe -m pip install -e '.[dev]'
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
```

En Linux/macOS sustituye `.\.venv\Scripts\python.exe` por `.venv/bin/python`.

## Documentación

- [Instalación y desinstalación](docs/INSTALACION.md)
- [Guía de uso y restricciones](docs/USO.md)
- [Arquitectura](docs/ARQUITECTURA.md)
- [Compilación, firma y empaquetado](docs/DISTRIBUCION.md)
- [Dependencias y licencias](docs/DEPENDENCIAS.md)
- [Ejemplo de resultados](examples/README.md)
- [Cambios](CHANGELOG.md)

La licencia del proyecto está pendiente de elección: consulta [LICENSE.template](LICENSE.template).
