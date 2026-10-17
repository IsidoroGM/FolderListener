# Verificación manual de una entrega

Registrar sistema, arquitectura, versión, SHA-256, usuario normal y resultado de cada
caso. Ejecutar en máquinas limpias independientes por plataforma, sin Python instalado.

1. Portátil: `--version`, `--help`, apertura del menú, acentos y conectores.
2. Selección: ruta con espacios/Unicode, raíz de unidad, unidad externa, ruta UNC/SMB
   accesible, carpeta inexistente y denegada. Verificar que no se solicitan credenciales
   ni privilegios. Probar navegación, subida, cambio de unidad, cancelación y tkinter.
3. En equipo sin pantalla o sin tkinter: comprobar explicación y continuación por consola.
4. Crear árbol con archivos, carpetas vacías, ocultos nativos, symlink, junction y ciclo.
   Comprobar exclusión sin entrar en destinos. Repetir las 2 profundidades, 3 selecciones
   y 4 representaciones y contrastar resultados con un inventario esperado.
5. Abrir TXT en editor UTF-8 y XLSX en Excel/LibreOffice. Verificar hoja Resumen, encabezados,
   anchos, congelación y que `=1+1.txt` es texto, no fórmula. Comprobar contexto en árbol.
6. Repetir generación: rechazar y aceptar sobrescritura. Cancelar al final y con Ctrl+C.
   Comparar hashes de salidas previas cuando se cancela. No deben aparecer temporales.
7. Simular disco lleno, Excel manteniendo abierto el resultado, carpeta retirada y permisos
   cambiantes. Comprobar preservación de salidas, mensaje y registro de procesos parciales.
8. Árbol grande real representativo: medir RAM, duración, espacio temporal y limpieza.
   La división de hojas y celdas largas se cubre además con límites reducidos en pytest.
9. Instalar en ubicación con espacios, ejecutar acceso directo/comando, reinstalar,
   desinstalar y comprobar conservación de los inventarios del usuario.
10. Verificar firma del editor, notarización/Gatekeeper en macOS o Authenticode en Windows
    si la entrega declara firma. Si no está firmada, registrar explícitamente ese estado.

Una prueba simulada de UNC o de permisos no sustituye la validación de un servidor real.
Las pruebas automatizadas crean fixtures propios y nunca usan carpetas personales como
material de prueba.
