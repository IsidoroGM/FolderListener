# Guía de uso

La raíz seleccionada no es una fila del inventario. Sus hijos están en nivel 1.
Primer nivel no entra en subcarpetas; recursiva recorre los niveles accesibles.
Solo archivos sigue atravesando carpetas para localizar archivos descendientes.

El orden es DFS: carpetas ordenadas alfabéticamente con sus descendientes y después
archivos del nivel, usando comparación sin mayúsculas y desempate por nombre exacto.
No se hace una ordenación global que mezcle niveles.

En árbol, las carpetas necesarias para mostrar la estructura con «solo archivos»
aparecen como `[contexto; no incluido]` en TXT. No cuentan ni aparecen como filas
Excel. Pueden mostrarse también carpetas vacías como contexto de la exploración.
En Excel la columna representación conserva conectores, pero sus filas son solo
elementos incluidos. La ruta relativa permite reconstruir la jerarquía completa.

Se excluyen nombres que empiezan por punto en todas las plataformas, atributos
Hidden/System de Windows, UF_HIDDEN de macOS, symlinks, junctions, reparse points y
archivos especiales. No se entra en directorios excluidos. Los enlaces duros de
archivos regulares son nombres válidos; no se leen sus contenidos.

Las rutas deben ser absolutas. Las unidades externas y UNC son válidas cuando el
sistema permite abrirlas. No se montan unidades ni se almacenan credenciales. Se
rechazan rutas con `..` o componentes enlazados; utilizar la ruta física real.
En macOS, por ejemplo, `/tmp` puede ser un enlace: usar `/private/tmp`.

## Salidas y cancelación

TXT contiene cabecera UTF-8, listado y resumen. Excel contiene `Resumen` y `Elementos`;
cada nueva hoja admite como máximo 1 048 575 entradas más cabecera. El resumen cuenta
la raíz como directorio explorado cuando se puede leer. La duración mide preparación,
exploración y emisión de filas, antes del cierre ZIP, confirmación y publicación.

La aplicación identifica todas las salidas reservadas existentes antes de solicitar
autorización. La denegación cancela sin modificarlas. Al terminar la preparación se
puede cancelar de nuevo antes de publicar. Ctrl+C también limpia los temporales.
Si una exportación falla, las salidas anteriores se conservan. Si falla una sustitución,
se intenta restaurar todas las versiones anteriores; si el propio sistema impide la
restauración, se indica la carpeta temporal que conserva las copias para recuperación.

Cada sustitución es atómica, pero el grupo de archivos no constituye una transacción
atómica frente a corte eléctrico o terminación forzada. No ejecutar dos generaciones
simultáneas sobre la misma raíz ni modificar sus salidas durante la publicación.
Las comprobaciones de versión detectan cambios anteriores al inicio de publicación;
no son un bloqueo distribuido para servidores de red. Los directorios no ofrecen una
instantánea: cambios concurrentes pueden producir omisiones, que se registran cuando
son detectables. No inventariar árboles que terceros hostiles estén modificando.

Un log histórico permanece intacto si el nuevo proceso no tiene incidencias. Su fecha
permite distinguirlo; el resumen actual y las rutas mostradas solo identifican archivos
de la ejecución actual. Las tres rutas reservadas siempre se excluyen del inventario.

## Texto y Excel

Todas las cadenas se escriben como celdas `data_type="s"`, formato de texto, incluso
si comienzan con `=`, `+`, `-` o `@`. No se agregan fórmulas ni vínculos externos.
El límite de celda se aplica en unidades UTF-16 (32 767); XML no admite ciertos
caracteres de control. Cada adaptación genera una incidencia y una línea adicional
con el valor completo en TXT. Los nombres POSIX con bytes no UTF-8 se conservan allí
como escapes de sustitutos Unicode, no como bytes UTF-8 inválidos.

El listado solo contiene nombres, rutas, atributos necesarios y estructura. Los
registros identifican rutas y operaciones, nunca contenidos. No hay telemetría,
actualizador, servicios, ejecución de archivos encontrados ni solicitudes de red.

La memoria depende del nivel más ancho y de los hermanos pendientes en la pila DFS.
Ordenar una sola carpeta con muchísimos hijos requiere memoria proporcional a ese
nivel. Excel usa temporales XML de openpyxl en el directorio temporal del sistema;
debe haber espacio suficiente tanto allí como en la raíz para ZIP/TXT y copias previas.
