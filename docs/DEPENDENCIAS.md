# Dependencias y revisión de licencias

Revisión realizada el 16 de octubre de 2026 sobre las versiones fijadas. El inventario
automático de cada entorno y los textos recogidos están en
`dist/THIRD_PARTY_NOTICES/inventory.json`. Distingue paquetes instalados para construir
de componentes realmente presentes en el ejecutable; el inventario no afirma que
todas las herramientas de desarrollo se redistribuyan.

| Componente | Versión | Papel | Licencia revisada |
|---|---|---|---|
| Python | 3.12.11 | Runtime incluido | PSF y avisos de terceros del intérprete |
| openpyxl | 3.1.5 | Escritura Excel | MIT |
| et-xmlfile | 2.0.0 | XML incremental | MIT; incluye LICENCE.python para código derivado de Python |
| Tcl/Tk | Según intérprete | Selector opcional | Avisos Tcl/Tk incluidos en `license.terms` |
| pytest | 8.4.2 | Pruebas | MIT |
| Ruff | 0.13.2 | Estilo y análisis | MIT, texto instalado |
| PyInstaller | 6.16.0 | Empaquetado | GPL-2.0-or-later con excepción de bootloader; determinados archivos Apache-2.0 |
| pyinstaller-hooks-contrib | 2026.8 | Hooks | GPL-2.0-or-later para construcción; Apache-2.0 para runtime hooks |
| altgraph | 0.17.5 | Construcción | MIT |
| pefile | 2023.2.7 | Construcción Windows | MIT |
| pywin32-ctypes | 0.2.3 | Construcción Windows | BSD-3-Clause |
| build / pyproject-hooks | 1.3.0 / 1.3.3 | Paquetes Python | MIT |
| setuptools | 80.9.0 | Construcción | MIT y licencias propias de componentes vendorizados |
| wheel | 0.45.1 | Construcción | MIT y licencias del packaging vendorizado |
| packaging | 26.3 | Herramientas | Apache-2.0 OR BSD-2-Clause |
| pluggy / iniconfig | 1.7.0 / 2.3.1 | Pruebas | MIT |
| Pygments | 2.21.0 | Pruebas | BSD-2-Clause |
| colorama | 0.4.6 | Herramientas Windows | BSD-3-Clause, texto instalado |
| macholib | 1.16.3 | Construcción macOS | MIT declarada; revisar texto en construcción nativa |
| Inno Setup | 6.7.3 | Instalador Windows | Licencia propia Inno Setup |

Las dos dependencias de ejecución declaran MIT en sus metadatos y documentación.
Los textos completos obtenidos de los archivos fuente oficiales se conservan en
`licenses/`. Fuentes y SHA-256 de los sdists descargados desde PyPI:

- `openpyxl-3.1.5.tar.gz`:
  `cf0e3cf56142039133628b5acffe8ef0c12bc902d2aadd3e0fe5878dc08d1050`.
- `et_xmlfile-2.0.0.tar.gz`:
  `dab3f4764309081ce75662649be815c4c9081e88f0837825f90fd28317d4da54`.

MIT/BSD requieren conservar los avisos y textos aplicables. La excepción de
[PyInstaller](https://pyinstaller.org/en/stable/license.html) permite empaquetar
aplicaciones comerciales, sin eliminar las obligaciones de sus dependencias.
Se han recogido también los textos de los hooks y componentes vendorizados presentes.

La [licencia publicada de Inno Setup](https://jrsoftware.org/files/is/license.txt)
permite uso comercial con condiciones de conservación de avisos y atribución de origen.
Su [página de descarga](https://jrsoftware.org/isdl.php) solicita adquirir licencia
comercial; revisar las condiciones de la versión usada y la política de la organización
antes de comercializar. No se ha comprado ninguna licencia ni firmado ningún producto.

## Pendientes antes de recomendar distribución comercial

- Elegir la licencia y el titular de FolderLister, sustituyendo `LICENSE.template`.
- Revisar el inventario binario final de cada plataforma (DLL/dylib/SO, Python,
  Tcl/Tk, runtimes Microsoft y bibliotecas embebidas) y sus obligaciones específicas.
- Revisar `macholib` y avisos nativos de macOS/Linux en los equipos de compilación;
  no se han instalado ni auditado aquí esos entornos.
- Mantener los avisos de terceros junto a la entrega y actualizar esta revisión
  cuando cambien versiones, herramientas o bibliotecas incluidas.

No se presenta esta revisión técnica de metadatos y textos como autorización jurídica
definitiva ni como auditoría binaria exhaustiva de plataformas aún no construidas.
