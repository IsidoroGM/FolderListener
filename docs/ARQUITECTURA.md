# Diseño de FolderLister 1.0

Flujo: CLI → Session → controlador → generador de Entry → TXT + XLSX → publicación.

`models` define entradas inmutables, contadores, resultados y cancelaciones. `config`
conserva opciones únicamente en memoria. `selection` valida rutas y ofrece navegación
y selector opcional. `filesystem` protege aperturas de directorios. `filters` decide
exclusiones. `scanner` ordena cada nivel y realiza DFS iterativo. `rendering` comparte
la representación entre exportadores. `issues` registra incidencias incrementalmente.
`transaction` prepara salidas y recupera versiones anteriores si falla una sustitución.
`controller` coordina recursos, cancelación y publicación. `cli` contiene los diálogos.

Se ordenan carpetas y archivos por `(nombre.casefold(), nombre)`. Cada carpeta aparece
antes de su descendencia; tras las carpetas de un nivel vienen sus archivos. Se guarda
un nivel ordenado por cada marco DFS activo: memoria proporcional a hermanos pendientes
y profundidad, no al árbol entero. Los iteradores de scandir se cierran antes de emitir.
Las carpetas de contexto del modo árbol se marcan y no se exportan como filas Excel.
Las identidades físicas de la rama activa detectan ciclos de montaje sin conservar
un conjunto de todos los directorios del árbol. Cuando el sistema no aporta inode
válido se conserva la protección de aperturas sin enlaces, sin inventar identidades.

Los directorios se abren sin seguir enlaces. En POSIX se usan descriptores y O_NOFOLLOW
para cada componente; en Windows se fijan los componentes mediante handles que no
comparten eliminación y se rechazan todos los reparse points. Esto también rechaza
rutas elegidas cuyos ancestros sean enlaces, una restricción deliberada de seguridad.

Las salidas se generan en un directorio temporal propio dentro de la raíz, que además
prueba la escritura antes del recorrido. Se confirman sobrescrituras antes de generar,
y se verifica que las salidas no hayan cambiado antes de publicar. Las sustituciones
son atómicas por archivo, con restauración ante excepciones; ningún sistema portátil
ofrece atomicidad conjunta de TXT/XLSX/log frente a apagados. No se leen contenidos
de archivos inventariados. Los backups mueven exclusivamente salidas autorizadas.
