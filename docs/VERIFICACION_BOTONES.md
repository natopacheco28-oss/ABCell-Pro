# Verificación de botones — ABCell

Geometría Qt y caja de contenido de botones; no sustituye prueba física de hardware ni revisión manual en Windows.

Evidencia: GitHub Actions, commit `83c5674`, Python 3.12 y PySide6, escalas 100 %, 150 % y 200 %.

Se comprobaron 168 combinaciones de botón y sección, con cobertura contra el código fuente. Resoluciones lógicas: 900×600, 1366×768 y 1920×1080.

Medidas en píxeles lógicos. Los controles fuera del viewport se alcanzan mediante scroll.

| Pantalla / sección | Botón | Mínimo ancho × alto | Verificación geométrica |
|---|---|---|---|
| Órdenes de trabajo | Órdenes de trabajo | 220 × 48 | Sin recorte de contenido |
| Órdenes de trabajo | Nueva orden | 169 × 48 | Sin recorte de contenido |
| Órdenes de trabajo | Inventario | 149 × 48 | Sin recorte de contenido |
| Órdenes de trabajo | Catálogo y Ubicaciones | 251 × 48 | Sin recorte de contenido |
| Órdenes de trabajo | Estadísticas y Caja | 215 × 48 | Sin recorte de contenido |
| Órdenes de trabajo | Utilidades Android | 215 × 48 | Sin recorte de contenido |
| Órdenes de trabajo | Configuración de taller | 248 × 48 | Sin recorte de contenido |
| Órdenes de trabajo | Todas | 85 × 44 | Sin recorte de contenido |
| Órdenes de trabajo | Entrada | 102 × 44 | Sin recorte de contenido |
| Órdenes de trabajo | Reparación | 129 × 44 | Sin recorte de contenido |
| Órdenes de trabajo | Salida | 89 × 44 | Sin recorte de contenido |
| Órdenes de trabajo | Guardar Estado / Ubicación | 282 × 44 | Sin recorte de contenido |
| Órdenes de trabajo | Editar orden | 166 × 44 | Sin recorte de contenido |
| Órdenes de trabajo | Registrar Abono | 196 × 44 | Sin recorte de contenido |
| Órdenes de trabajo | Imprimir ticket | 185 × 44 | Sin recorte de contenido |
| Órdenes de trabajo | Ticket digital | 171 × 44 | Sin recorte de contenido |
| Órdenes de trabajo | Eliminar orden | 184 × 44 | Sin recorte de contenido |
| Nueva orden | Órdenes de trabajo | 220 × 48 | Sin recorte de contenido |
| Nueva orden | Nueva orden | 169 × 48 | Sin recorte de contenido |
| Nueva orden | Inventario | 149 × 48 | Sin recorte de contenido |
| Nueva orden | Catálogo y Ubicaciones | 251 × 48 | Sin recorte de contenido |
| Nueva orden | Estadísticas y Caja | 215 × 48 | Sin recorte de contenido |
| Nueva orden | Utilidades Android | 215 × 48 | Sin recorte de contenido |
| Nueva orden | Configuración de taller | 248 × 48 | Sin recorte de contenido |
| Nueva orden | Borrar patrón | 176 × 44 | Sin recorte de contenido |
| Nueva orden | Limpiar | 127 × 44 | Sin recorte de contenido |
| Nueva orden | Guardar Orden | 185 × 44 | Sin recorte de contenido |
| Inventario | Órdenes de trabajo | 220 × 48 | Sin recorte de contenido |
| Inventario | Nueva orden | 169 × 48 | Sin recorte de contenido |
| Inventario | Inventario | 149 × 48 | Sin recorte de contenido |
| Inventario | Catálogo y Ubicaciones | 251 × 48 | Sin recorte de contenido |
| Inventario | Estadísticas y Caja | 215 × 48 | Sin recorte de contenido |
| Inventario | Utilidades Android | 215 × 48 | Sin recorte de contenido |
| Inventario | Configuración de taller | 248 × 48 | Sin recorte de contenido |
| Inventario | Desbloquear edición | 229 × 44 | Sin recorte de contenido |
| Inventario | Agregar producto | 208 × 44 | Sin recorte de contenido |
| Inventario | Restar 1 al stock | 56 × 44 | Sin recorte de contenido |
| Inventario | Sumar 1 al stock | 56 × 44 | Sin recorte de contenido |
| Inventario | Editar | 111 × 44 | Sin recorte de contenido |
| Inventario | Eliminar | 129 × 44 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Órdenes de trabajo | 220 × 48 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Nueva orden | 169 × 48 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Inventario | 149 × 48 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Catálogo y Ubicaciones | 251 × 48 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Estadísticas y Caja | 215 × 48 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Utilidades Android | 215 × 48 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Configuración de taller | 248 × 48 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Agregar servicio | 198 × 44 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Editar | 111 × 44 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Eliminar | 129 × 44 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Órdenes de trabajo | 220 × 48 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Nueva orden | 169 × 48 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Inventario | 149 × 48 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Catálogo y Ubicaciones | 251 × 48 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Estadísticas y Caja | 215 × 48 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Utilidades Android | 215 × 48 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Configuración de taller | 248 × 48 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Agregar ubicación | 212 × 44 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Editar | 111 × 44 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Eliminar | 129 × 44 | Sin recorte de contenido |
| Estadísticas y Caja | Órdenes de trabajo | 220 × 48 | Sin recorte de contenido |
| Estadísticas y Caja | Nueva orden | 169 × 48 | Sin recorte de contenido |
| Estadísticas y Caja | Inventario | 149 × 48 | Sin recorte de contenido |
| Estadísticas y Caja | Catálogo y Ubicaciones | 251 × 48 | Sin recorte de contenido |
| Estadísticas y Caja | Estadísticas y Caja | 215 × 48 | Sin recorte de contenido |
| Estadísticas y Caja | Utilidades Android | 215 × 48 | Sin recorte de contenido |
| Estadísticas y Caja | Configuración de taller | 248 × 48 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Órdenes de trabajo | 220 × 48 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Nueva orden | 169 × 48 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Inventario | 149 × 48 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Catálogo y Ubicaciones | 251 × 48 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Estadísticas y Caja | 215 × 48 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Utilidades Android | 215 × 48 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Configuración de taller | 248 × 48 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Detectar equipos | 204 × 44 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Reiniciar ADB | 175 × 44 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Ejecutar diagnóstico completo | 307 × 44 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Copiar reporte | 183 × 44 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Captura de pantalla | 224 × 44 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Enviar a Nueva Orden | 240 × 44 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Reiniciar equipo | 196 × 44 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Limpiar registro | 195 × 44 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Órdenes de trabajo | 220 × 48 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Nueva orden | 169 × 48 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Inventario | 149 × 48 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Catálogo y Ubicaciones | 251 × 48 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Estadísticas y Caja | 215 × 48 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Utilidades Android | 215 × 48 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Configuración de taller | 248 × 48 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Detectar equipos | 204 × 44 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Reiniciar ADB | 175 × 44 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Escanear aplicaciones | 242 × 44 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | ¿Qué app está en pantalla? | 282 × 44 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Marcar sospechosas | 227 × 44 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Desmarcar todo | 194 × 44 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Bloquear anuncios flotantes | 289 × 44 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Limpiar notificaciones spam de Chrome | 379 × 44 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Desactivar marcadas | 233 × 44 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Desinstalar marcadas | 239 × 44 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Limpiar registro | 195 × 44 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Órdenes de trabajo | 220 × 48 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Nueva orden | 169 × 48 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Inventario | 149 × 48 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Catálogo y Ubicaciones | 251 × 48 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Estadísticas y Caja | 215 × 48 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Utilidades Android | 215 × 48 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Configuración de taller | 248 × 48 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Detectar equipos | 204 × 44 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Reiniciar ADB | 175 × 44 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Leer DNS actual | 194 × 44 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Anclar DNS en el equipo | 259 × 44 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Probar conexión DNS | 235 × 44 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Restaurar DNS automático | 278 × 44 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Desactivar DNS privado | 255 × 44 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Limpiar registro | 195 × 44 | Sin recorte de contenido |
| Configuración de taller | Órdenes de trabajo | 220 × 48 | Sin recorte de contenido |
| Configuración de taller | Nueva orden | 169 × 48 | Sin recorte de contenido |
| Configuración de taller | Inventario | 149 × 48 | Sin recorte de contenido |
| Configuración de taller | Catálogo y Ubicaciones | 251 × 48 | Sin recorte de contenido |
| Configuración de taller | Estadísticas y Caja | 215 × 48 | Sin recorte de contenido |
| Configuración de taller | Utilidades Android | 215 × 48 | Sin recorte de contenido |
| Configuración de taller | Configuración de taller | 248 × 48 | Sin recorte de contenido |
| Configuración de taller | Probar impresión | 204 × 44 | Sin recorte de contenido |
| Configuración de taller | Cambiar tema visual | 62 × 46 | Sin recorte de contenido |
| Configuración de taller | Elegir logo | 152 × 44 | Sin recorte de contenido |
| Configuración de taller | Insertar texto de ejemplo | 269 × 44 | Sin recorte de contenido |
| Configuración de taller | Guardar Configuración | 246 × 44 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Órdenes de trabajo | 220 × 48 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Nueva orden | 169 × 48 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Inventario | 149 × 48 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Catálogo y Ubicaciones | 251 × 48 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Estadísticas y Caja | 215 × 48 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Utilidades Android | 215 × 48 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Configuración de taller | 248 × 48 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Bloquear edición | 229 × 44 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Agregar producto | 208 × 44 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Restar 1 al stock | 56 × 44 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Sumar 1 al stock | 56 × 44 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Editar | 111 × 44 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Eliminar | 129 × 44 | Sin recorte de contenido |
| Diálogo/Editar orden #0001 | Cancelar | 137 × 44 | Sin recorte de contenido |
| Diálogo/Editar orden #0001 | Guardar cambios | 202 × 44 | Sin recorte de contenido |
| Diálogo/Editar servicio | Cancelar | 137 × 44 | Sin recorte de contenido |
| Diálogo/Editar servicio | Guardar cambios | 202 × 44 | Sin recorte de contenido |
| Diálogo/Editar ubicación | Cancelar | 137 × 44 | Sin recorte de contenido |
| Diálogo/Editar ubicación | Guardar cambios | 202 × 44 | Sin recorte de contenido |
| Diálogo/Agregar producto al inventario | Cancelar | 137 × 44 | Sin recorte de contenido |
| Diálogo/Agregar producto al inventario | Guardar producto | 208 × 44 | Sin recorte de contenido |
| Diálogo/Editar producto | Cancelar | 137 × 44 | Sin recorte de contenido |
| Diálogo/Editar producto | Guardar cambios | 202 × 44 | Sin recorte de contenido |
| Diálogo/Ticket digital — Folio #0001 | Abrir imagen | 171 × 44 | Sin recorte de contenido |
| Diálogo/Ticket digital — Folio #0001 | Abrir carpeta | 173 × 44 | Sin recorte de contenido |
| Diálogo/Ticket digital — Folio #0001 | Enviar por WhatsApp | 235 × 44 | Sin recorte de contenido |
| Diálogo/Ticket digital — Folio #0001 | Cerrar | 118 × 44 | Sin recorte de contenido |
| Diálogo/Captura de pantalla del equipo | Abrir imagen | 171 × 44 | Sin recorte de contenido |
| Diálogo/Captura de pantalla del equipo | Abrir carpeta | 173 × 44 | Sin recorte de contenido |
| Diálogo/Captura de pantalla del equipo | Cerrar | 118 × 44 | Sin recorte de contenido |
| Diálogo/Modo maestro | Cerrar | 118 × 44 | Sin recorte de contenido |
| Diálogo/Modo maestro | Borrar todas las órdenes | 263 × 44 | Sin recorte de contenido |
| Diálogo/Modo maestro | Restablecer base de datos completa | 355 × 44 | Sin recorte de contenido |
| Diálogo/Modo maestro | Cambiar código maestro | 261 × 44 | Sin recorte de contenido |
| Diálogo/Mensajes estándar | Aceptar | 102 × 44 | Sin recorte de contenido |
| Diálogo/Mensajes estándar | Sí | 55 × 44 | Sin recorte de contenido |
| Diálogo/Mensajes estándar | No | 61 × 44 | Sin recorte de contenido |
| Diálogo/Código maestro | Aceptar | 102 × 44 | Sin recorte de contenido |
| Diálogo/Código maestro | Cancelar | 109 × 44 | Sin recorte de contenido |
| Diálogo/Archivos Qt | Abrir | 79 × 44 | Sin recorte de contenido |
| Diálogo/Archivos Qt | Cancelar | 109 × 44 | Sin recorte de contenido |

## Retirados

- Elegir adb.exe
- ¿Cómo conectar por USB?
- Refrescar datos

## Incidencias

Ninguna incidencia geométrica de botones en las condiciones probadas.
