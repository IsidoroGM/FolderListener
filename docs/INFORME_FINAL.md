# Informe de entrega — FolderLister 1.0.0

Fecha: 16 de octubre de 2026.

## Implementación

Proyecto Python instalable con estructura `src/folderlister`, 15 módulos de aplicación,
modelos tipados y configuración de sesión. Menú español, tres selectores de directorio,
recorrido iterativo, filtros nativos, orden jerárquico, cuatro representaciones y
exportadores incrementales TXT/XLSX. El controlador confirma sobrescrituras, prueba
escritura antes del recorrido, admite cancelación antes de publicar y restaura salidas
previas cuando falla una sustitución.

Excel escribe texto literal y reparte filas en hojas adicionales. Las adaptaciones de
longitud/XML se registran y conservan valores completos en TXT. Los errores recuperables
producen un resultado parcial y un registro con rutas, operación, fecha y diagnóstico.

## Verificaciones realizadas

Entorno real: Windows 10 22H2, compilación 19045, AMD64; CPython 3.12.11 local.

| Verificación | Resultado observado |
|---|---|
| pytest, código final | **46 correctas, 1 omitida**, 15,51 s |
| Ruff check | Sin errores |
| Ruff format --check | 25 archivos Python con formato correcto |
| Exportación grande sintética | 20 000 entradas, 4 hojas de elementos de 5 000 filas cada una |
| Profundidad sintética | 1 100 niveles, sin recursión de llamadas |
| Atributo Hidden y junction Windows | Creación real, exclusión y rechazo de raíz enlazada comprobados |
| Ciclo por identidad física | Montaje cíclico simulado detenido sin recorrer la rama repetida |
| Permisos, desapariciones y red UNC | Pruebas simuladas de fallos y validación |
| Cancelación, fallos de exportación/publicación | Salidas anteriores conservadas; temporales eliminados |
| XLSX | Reapertura, conteos, valores literales y hojas comprobados con openpyxl |
| PyInstaller 6.16.0 | Ejecutable Windows x64 construido y `--version` correcto |
| Portátil empaquetado | Menú real, ruta con ñ, TXT/XLSX y rechazo de sobrescritura correctos |
| Inno Setup 6.7.3 | Instalador compilado correctamente |
| Instalador real | Instalación local de prueba, ejecución funcional y desinstalación correctas |
| Firmas de FolderLister | Sin firma digital; no se declara firmado |

El único caso omitido es la creación de symlinks: este usuario no dispone del permiso
necesario en Windows. El rechazo de junctions/reparse points se verificó por separado
con una unión real. La primera prueba detectó una apertura de solo lectura incompatible
con `fsync` en Windows; se corrigió a `r+b` y se repitió la batería con éxito.

Las pruebas nativas se ejecutaron fuera del sandbox de herramientas porque este
impedía fijar handles de directorios ancestros. Los resultados de esas primeras pruebas
restringidas no se presentan como fallos de la versión final. Los temporales de pytest
se aislaron en `build/` para evitar conflictos de permisos entre usuarios de ejecución.

## Artefactos y evidencias

- `dist/FolderLister.exe`: portátil Windows x64, Python incluido.
- `dist/FolderLister-1.0.0-setup.exe`: instalador por usuario de Windows.
- `dist/build-manifest.json`: entorno y SHA-256 del portátil sin firmar.
- `dist/THIRD_PARTY_NOTICES/`: licencias e inventario del entorno de construcción.
- `dist/folderlister-1.0.0-py3-none-any.whl` y `dist/folderlister-1.0.0.tar.gz`:
  paquete instalable de Python y distribución del código fuente.
- `examples/Proyectos/`: entradas de ejemplo y TXT/XLSX generados por la aplicación.
- `build/test-results.xml`: resultado JUnit de pytest.
- `build/windows-build.log`, `build/inno-build.log`, `build/installer-smoke.log`:
  evidencias de compilación e instalación local.

Los scripts `build.py`, `build-windows.ps1`, `build-linux.sh` y `build-macos.sh`
automatizan construcciones nativas. `smoke.py` comprueba binarios y
`test-installer-windows.ps1` comprueba instalación/desinstalación sin modificar una
instalación anterior. `python -m build --no-isolation` prepara wheel y distribución fuente.

## Límites y validaciones pendientes

- No se han construido ni ejecutado binarios o instaladores de Linux/macOS. Sus scripts
  y trabajos de CI están preparados; el flujo GitHub Actions no se ha enviado ni ejecutado.
- La prueba de Windows se hizo en este equipo de desarrollo, no en una máquina limpia
  sin Python. El binario contiene su runtime, pero falta la matriz de aceptación externa.
- Tkinter queda integrado y dispone de fallback probado; el diálogo gráfico nativo no
  ha sido validado manualmente. Tampoco se han probado servidores UNC/SMB ni discos
  externos reales, ACL de producción, escenarios de disco lleno real o corte eléctrico.
- El máximo de Excel se comprueba mediante límites reducidos e inyectables; no se crearon
  millones de archivos. No se afirma un límite de RAM o rendimiento universal.
- Atomicidad por archivo y rollback ante excepciones; no atomicidad conjunta ante apagados.
  No usar generaciones concurrentes ni árboles modificados por terceros hostiles.
- Las rutas con ancestros enlazados se rechazan deliberadamente. La ordenación necesita
  almacenar hermanos de cada nivel activo, y Excel requiere espacio temporal en disco.
- No hay certificados, Authenticode del producto ni notarización. La licencia definitiva
  del producto y la auditoría binaria final por plataforma siguen pendientes; véase
  `DEPENDENCIAS.md`. No se recomienda aún una publicación comercial sin completar estos pasos.

El código y los artefactos Windows están disponibles para evaluación local. La validación
de cada plataforma es un requisito separado antes de una publicación pública en ella.
