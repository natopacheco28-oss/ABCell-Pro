# Verificación de botones — ABCell Pro

Revisión compacta `2343b7d`. Cada tabla enumera las 168 combinaciones botón/sección, incluyendo navegación repetida por pantalla, con sus mínimos calculados y confirmación geométrica. No es una prueba funcional de cada clic ni una certificación de hardware.

- Windows nativo: 21 pruebas aprobadas y 168 combinaciones sin incidencias. [Compilación y auditoría](https://github.com/natopacheco28-oss/ABCell-Pro/actions/runs/45664761224).
- Linux Qt offscreen: 21 pruebas y 168 combinaciones sin incidencias a escalas 100 %, 150 % y 200 %. [Ejecución](https://github.com/natopacheco28-oss/ABCell-Pro/actions/runs/45664760420).
- Resoluciones auditadas: 900×600, 1358×690, 1366×768 y 1920×1080. El catálogo tiene además una regresión específica a 1358×690 para comprobar sidebar ≤280 px, acciones visibles y ausencia de scroll horizontal con los datos de prueba.
- Tamaños en píxeles lógicos; mínimos generales 32 px y navegación 38 px. El texto puede exigir mayor tamaño. Las métricas varían por fuente/plataforma.
- Retirados de toda la interfaz: «Elegir adb.exe», «¿Cómo conectar por USB?» y «Refrescar datos».

Se comprobó además por píxeles que las etiquetas y sus contenedores muestran el fondo de la tarjeta en los seis temas, y que la firma de autor permanece visible dentro de la barra lateral. No se agregaron ni retiraron botones en esta revisión.

## Windows — fuente nativa

| Pantalla / sección | Botón | Mínimo ancho × alto | Verificación geométrica |
|---|---|---|---|
| Órdenes de trabajo | Órdenes de trabajo | 163 × 36 | Sin recorte de contenido |
| Órdenes de trabajo | Nueva orden | 125 × 36 | Sin recorte de contenido |
| Órdenes de trabajo | Inventario | 108 × 36 | Sin recorte de contenido |
| Órdenes de trabajo | Catálogo y Ubicaciones | 186 × 36 | Sin recorte de contenido |
| Órdenes de trabajo | Estadísticas y Caja | 155 × 36 | Sin recorte de contenido |
| Órdenes de trabajo | Utilidades Android | 158 × 36 | Sin recorte de contenido |
| Órdenes de trabajo | Configuración de taller | 184 × 36 | Sin recorte de contenido |
| Órdenes de trabajo | Todas | 59 × 32 | Sin recorte de contenido |
| Órdenes de trabajo | Entrada | 71 × 32 | Sin recorte de contenido |
| Órdenes de trabajo | Reparación | 91 × 32 | Sin recorte de contenido |
| Órdenes de trabajo | Salida | 59 × 32 | Sin recorte de contenido |
| Órdenes de trabajo | Guardar Estado / Ubicación | 211 × 32 | Sin recorte de contenido |
| Órdenes de trabajo | Editar orden | 125 × 32 | Sin recorte de contenido |
| Órdenes de trabajo | Registrar Abono | 145 × 32 | Sin recorte de contenido |
| Órdenes de trabajo | Imprimir ticket | 135 × 32 | Sin recorte de contenido |
| Órdenes de trabajo | Ticket digital | 125 × 32 | Sin recorte de contenido |
| Órdenes de trabajo | Eliminar orden | 134 × 32 | Sin recorte de contenido |
| Nueva orden | Órdenes de trabajo | 163 × 36 | Sin recorte de contenido |
| Nueva orden | Nueva orden | 125 × 36 | Sin recorte de contenido |
| Nueva orden | Inventario | 108 × 36 | Sin recorte de contenido |
| Nueva orden | Catálogo y Ubicaciones | 186 × 36 | Sin recorte de contenido |
| Nueva orden | Estadísticas y Caja | 155 × 36 | Sin recorte de contenido |
| Nueva orden | Utilidades Android | 158 × 36 | Sin recorte de contenido |
| Nueva orden | Configuración de taller | 184 × 36 | Sin recorte de contenido |
| Nueva orden | Borrar patrón | 130 × 32 | Sin recorte de contenido |
| Nueva orden | Limpiar | 115 × 32 | Sin recorte de contenido |
| Nueva orden | Guardar Orden | 145 × 32 | Sin recorte de contenido |
| Inventario | Órdenes de trabajo | 163 × 36 | Sin recorte de contenido |
| Inventario | Nueva orden | 125 × 36 | Sin recorte de contenido |
| Inventario | Inventario | 108 × 36 | Sin recorte de contenido |
| Inventario | Catálogo y Ubicaciones | 186 × 36 | Sin recorte de contenido |
| Inventario | Estadísticas y Caja | 155 × 36 | Sin recorte de contenido |
| Inventario | Utilidades Android | 158 × 36 | Sin recorte de contenido |
| Inventario | Configuración de taller | 184 × 36 | Sin recorte de contenido |
| Inventario | Desbloquear edición | 169 × 32 | Sin recorte de contenido |
| Inventario | Agregar producto | 165 × 32 | Sin recorte de contenido |
| Inventario | Restar 1 al stock | 44 × 32 | Sin recorte de contenido |
| Inventario | Sumar 1 al stock | 44 × 32 | Sin recorte de contenido |
| Inventario | Editar | 79 × 32 | Sin recorte de contenido |
| Inventario | Eliminar | 92 × 32 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Órdenes de trabajo | 163 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Nueva orden | 125 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Inventario | 108 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Catálogo y Ubicaciones | 186 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Estadísticas y Caja | 155 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Utilidades Android | 158 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Configuración de taller | 184 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Agregar servicio | 150 × 32 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Editar | 79 × 32 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Eliminar | 92 × 32 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Órdenes de trabajo | 163 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Nueva orden | 125 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Inventario | 108 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Catálogo y Ubicaciones | 186 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Estadísticas y Caja | 155 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Utilidades Android | 158 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Configuración de taller | 184 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Agregar ubicación | 160 × 32 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Editar | 79 × 32 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Eliminar | 92 × 32 | Sin recorte de contenido |
| Estadísticas y Caja | Órdenes de trabajo | 163 × 36 | Sin recorte de contenido |
| Estadísticas y Caja | Nueva orden | 125 × 36 | Sin recorte de contenido |
| Estadísticas y Caja | Inventario | 108 × 36 | Sin recorte de contenido |
| Estadísticas y Caja | Catálogo y Ubicaciones | 186 × 36 | Sin recorte de contenido |
| Estadísticas y Caja | Estadísticas y Caja | 155 × 36 | Sin recorte de contenido |
| Estadísticas y Caja | Utilidades Android | 158 × 36 | Sin recorte de contenido |
| Estadísticas y Caja | Configuración de taller | 184 × 36 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Órdenes de trabajo | 163 × 36 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Nueva orden | 125 × 36 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Inventario | 108 × 36 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Catálogo y Ubicaciones | 186 × 36 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Estadísticas y Caja | 155 × 36 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Utilidades Android | 158 × 36 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Configuración de taller | 184 × 36 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Detectar equipos | 150 × 32 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Reiniciar ADB | 126 × 32 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Ejecutar diagnóstico completo | 250 × 32 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Copiar reporte | 134 × 32 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Captura de pantalla | 165 × 32 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Enviar a Nueva Orden | 179 × 32 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Reiniciar equipo | 142 × 32 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Limpiar registro | 141 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Órdenes de trabajo | 163 × 36 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Nueva orden | 125 × 36 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Inventario | 108 × 36 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Catálogo y Ubicaciones | 186 × 36 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Estadísticas y Caja | 155 × 36 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Utilidades Android | 158 × 36 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Configuración de taller | 184 × 36 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Detectar equipos | 150 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Reiniciar ADB | 126 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Escanear aplicaciones | 190 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | ¿Qué app está en pantalla? | 210 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Marcar sospechosas | 168 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Desmarcar todo | 143 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Bloquear anuncios flotantes | 216 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Limpiar notificaciones spam de Chrome | 285 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Desactivar marcadas | 170 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Desinstalar marcadas | 175 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Limpiar registro | 141 × 32 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Órdenes de trabajo | 163 × 36 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Nueva orden | 125 × 36 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Inventario | 108 × 36 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Catálogo y Ubicaciones | 186 × 36 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Estadísticas y Caja | 155 × 36 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Utilidades Android | 158 × 36 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Configuración de taller | 184 × 36 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Detectar equipos | 150 × 32 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Reiniciar ADB | 126 × 32 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Leer DNS actual | 141 × 32 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Anclar DNS en el equipo | 195 × 32 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Probar conexión DNS | 176 × 32 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Restaurar DNS automático | 207 × 32 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Desactivar DNS privado | 188 × 32 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Limpiar registro | 141 × 32 | Sin recorte de contenido |
| Configuración de taller | Órdenes de trabajo | 163 × 36 | Sin recorte de contenido |
| Configuración de taller | Nueva orden | 125 × 36 | Sin recorte de contenido |
| Configuración de taller | Inventario | 108 × 36 | Sin recorte de contenido |
| Configuración de taller | Catálogo y Ubicaciones | 186 × 36 | Sin recorte de contenido |
| Configuración de taller | Estadísticas y Caja | 155 × 36 | Sin recorte de contenido |
| Configuración de taller | Utilidades Android | 158 × 36 | Sin recorte de contenido |
| Configuración de taller | Configuración de taller | 184 × 36 | Sin recorte de contenido |
| Configuración de taller | Probar impresión | 160 × 32 | Sin recorte de contenido |
| Configuración de taller | Cambiar tema visual | 50 × 36 | Sin recorte de contenido |
| Configuración de taller | Elegir logo | 110 × 32 | Sin recorte de contenido |
| Configuración de taller | Insertar texto de ejemplo | 200 × 32 | Sin recorte de contenido |
| Configuración de taller | Guardar Configuración | 195 × 32 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Órdenes de trabajo | 163 × 36 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Nueva orden | 125 × 36 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Inventario | 108 × 36 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Catálogo y Ubicaciones | 186 × 36 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Estadísticas y Caja | 155 × 36 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Utilidades Android | 158 × 36 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Configuración de taller | 184 × 36 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Bloquear edición | 169 × 32 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Agregar producto | 165 × 32 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Restar 1 al stock | 44 × 32 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Sumar 1 al stock | 44 × 32 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Editar | 79 × 32 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Eliminar | 92 × 32 | Sin recorte de contenido |
| Diálogo/Editar orden #0001 | Cancelar | 97 × 32 | Sin recorte de contenido |
| Diálogo/Editar orden #0001 | Guardar cambios | 150 × 32 | Sin recorte de contenido |
| Diálogo/Editar servicio | Cancelar | 97 × 32 | Sin recorte de contenido |
| Diálogo/Editar servicio | Guardar cambios | 149 × 32 | Sin recorte de contenido |
| Diálogo/Editar ubicación | Cancelar | 97 × 32 | Sin recorte de contenido |
| Diálogo/Editar ubicación | Guardar cambios | 149 × 32 | Sin recorte de contenido |
| Diálogo/Agregar producto al inventario | Cancelar | 97 × 32 | Sin recorte de contenido |
| Diálogo/Agregar producto al inventario | Guardar producto | 155 × 32 | Sin recorte de contenido |
| Diálogo/Editar producto | Cancelar | 97 × 32 | Sin recorte de contenido |
| Diálogo/Editar producto | Guardar cambios | 150 × 32 | Sin recorte de contenido |
| Diálogo/Ticket digital — Folio #0001 | Abrir imagen | 125 × 32 | Sin recorte de contenido |
| Diálogo/Ticket digital — Folio #0001 | Abrir carpeta | 125 × 32 | Sin recorte de contenido |
| Diálogo/Ticket digital — Folio #0001 | Enviar por WhatsApp | 176 × 32 | Sin recorte de contenido |
| Diálogo/Ticket digital — Folio #0001 | Cerrar | 83 × 32 | Sin recorte de contenido |
| Diálogo/Captura de pantalla del equipo | Abrir imagen | 125 × 32 | Sin recorte de contenido |
| Diálogo/Captura de pantalla del equipo | Abrir carpeta | 125 × 32 | Sin recorte de contenido |
| Diálogo/Captura de pantalla del equipo | Cerrar | 83 × 32 | Sin recorte de contenido |
| Diálogo/Modo maestro | Cerrar | 83 × 32 | Sin recorte de contenido |
| Diálogo/Modo maestro | Borrar todas las órdenes | 195 × 32 | Sin recorte de contenido |
| Diálogo/Modo maestro | Restablecer base de datos completa | 264 × 32 | Sin recorte de contenido |
| Diálogo/Modo maestro | Cambiar código maestro | 195 × 32 | Sin recorte de contenido |
| Diálogo/Mensajes estándar | Aceptar | 71 × 32 | Sin recorte de contenido |
| Diálogo/Mensajes estándar | Sí | 35 × 32 | Sin recorte de contenido |
| Diálogo/Mensajes estándar | No | 42 × 32 | Sin recorte de contenido |
| Diálogo/Código maestro | Aceptar | 71 × 32 | Sin recorte de contenido |
| Diálogo/Código maestro | Cancelar | 75 × 32 | Sin recorte de contenido |
| Diálogo/Archivos Qt | Abrir | 54 × 32 | Sin recorte de contenido |
| Diálogo/Archivos Qt | Cancelar | 75 × 32 | Sin recorte de contenido |

## Retirados

- Elegir adb.exe
- ¿Cómo conectar por USB?
- Refrescar datos

## Incidencias

Ninguna incidencia geométrica de botones en las condiciones probadas.

## Linux — escala 100 %

| Pantalla / sección | Botón | Mínimo ancho × alto | Verificación geométrica |
|---|---|---|---|
| Órdenes de trabajo | Órdenes de trabajo | 187 × 36 | Sin recorte de contenido |
| Órdenes de trabajo | Nueva orden | 139 × 36 | Sin recorte de contenido |
| Órdenes de trabajo | Inventario | 121 × 36 | Sin recorte de contenido |
| Órdenes de trabajo | Catálogo y Ubicaciones | 216 × 36 | Sin recorte de contenido |
| Órdenes de trabajo | Estadísticas y Caja | 183 × 36 | Sin recorte de contenido |
| Órdenes de trabajo | Utilidades Android | 182 × 36 | Sin recorte de contenido |
| Órdenes de trabajo | Configuración de taller | 214 × 36 | Sin recorte de contenido |
| Órdenes de trabajo | Todas | 66 × 32 | Sin recorte de contenido |
| Órdenes de trabajo | Entrada | 82 × 32 | Sin recorte de contenido |
| Órdenes de trabajo | Reparación | 107 × 32 | Sin recorte de contenido |
| Órdenes de trabajo | Salida | 70 × 32 | Sin recorte de contenido |
| Órdenes de trabajo | Guardar Estado / Ubicación | 245 × 32 | Sin recorte de contenido |
| Órdenes de trabajo | Editar orden | 137 × 32 | Sin recorte de contenido |
| Órdenes de trabajo | Registrar Abono | 165 × 32 | Sin recorte de contenido |
| Órdenes de trabajo | Imprimir ticket | 155 × 32 | Sin recorte de contenido |
| Órdenes de trabajo | Ticket digital | 142 × 32 | Sin recorte de contenido |
| Órdenes de trabajo | Eliminar orden | 153 × 32 | Sin recorte de contenido |
| Nueva orden | Órdenes de trabajo | 187 × 36 | Sin recorte de contenido |
| Nueva orden | Nueva orden | 139 × 36 | Sin recorte de contenido |
| Nueva orden | Inventario | 121 × 36 | Sin recorte de contenido |
| Nueva orden | Catálogo y Ubicaciones | 216 × 36 | Sin recorte de contenido |
| Nueva orden | Estadísticas y Caja | 183 × 36 | Sin recorte de contenido |
| Nueva orden | Utilidades Android | 182 × 36 | Sin recorte de contenido |
| Nueva orden | Configuración de taller | 214 × 36 | Sin recorte de contenido |
| Nueva orden | Borrar patrón | 146 × 32 | Sin recorte de contenido |
| Nueva orden | Limpiar | 115 × 32 | Sin recorte de contenido |
| Nueva orden | Guardar Orden | 155 × 32 | Sin recorte de contenido |
| Inventario | Órdenes de trabajo | 187 × 36 | Sin recorte de contenido |
| Inventario | Nueva orden | 139 × 36 | Sin recorte de contenido |
| Inventario | Inventario | 121 × 36 | Sin recorte de contenido |
| Inventario | Catálogo y Ubicaciones | 216 × 36 | Sin recorte de contenido |
| Inventario | Estadísticas y Caja | 183 × 36 | Sin recorte de contenido |
| Inventario | Utilidades Android | 182 × 36 | Sin recorte de contenido |
| Inventario | Configuración de taller | 214 × 36 | Sin recorte de contenido |
| Inventario | Desbloquear edición | 196 × 32 | Sin recorte de contenido |
| Inventario | Agregar producto | 176 × 32 | Sin recorte de contenido |
| Inventario | Restar 1 al stock | 44 × 32 | Sin recorte de contenido |
| Inventario | Sumar 1 al stock | 44 × 32 | Sin recorte de contenido |
| Inventario | Editar | 88 × 32 | Sin recorte de contenido |
| Inventario | Eliminar | 104 × 32 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Órdenes de trabajo | 187 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Nueva orden | 139 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Inventario | 121 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Catálogo y Ubicaciones | 216 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Estadísticas y Caja | 183 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Utilidades Android | 182 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Configuración de taller | 214 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Agregar servicio | 167 × 32 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Editar | 88 × 32 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Servicios | Eliminar | 104 × 32 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Órdenes de trabajo | 187 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Nueva orden | 139 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Inventario | 121 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Catálogo y Ubicaciones | 216 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Estadísticas y Caja | 183 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Utilidades Android | 182 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Configuración de taller | 214 × 36 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Agregar ubicación | 179 × 32 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Editar | 88 × 32 | Sin recorte de contenido |
| Catálogo y Ubicaciones/Ubicaciones | Eliminar | 104 × 32 | Sin recorte de contenido |
| Estadísticas y Caja | Órdenes de trabajo | 187 × 36 | Sin recorte de contenido |
| Estadísticas y Caja | Nueva orden | 139 × 36 | Sin recorte de contenido |
| Estadísticas y Caja | Inventario | 121 × 36 | Sin recorte de contenido |
| Estadísticas y Caja | Catálogo y Ubicaciones | 216 × 36 | Sin recorte de contenido |
| Estadísticas y Caja | Estadísticas y Caja | 183 × 36 | Sin recorte de contenido |
| Estadísticas y Caja | Utilidades Android | 182 × 36 | Sin recorte de contenido |
| Estadísticas y Caja | Configuración de taller | 214 × 36 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Órdenes de trabajo | 187 × 36 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Nueva orden | 139 × 36 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Inventario | 121 × 36 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Catálogo y Ubicaciones | 216 × 36 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Estadísticas y Caja | 183 × 36 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Utilidades Android | 182 × 36 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Configuración de taller | 214 × 36 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Detectar equipos | 172 × 32 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Reiniciar ADB | 146 × 32 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Ejecutar diagnóstico completo | 268 × 32 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Copiar reporte | 153 × 32 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Captura de pantalla | 191 × 32 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Enviar a Nueva Orden | 206 × 32 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Reiniciar equipo | 165 × 32 | Sin recorte de contenido |
| Utilidades Android/Diagnóstico ADB | Limpiar registro | 164 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Órdenes de trabajo | 187 × 36 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Nueva orden | 139 × 36 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Inventario | 121 × 36 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Catálogo y Ubicaciones | 216 × 36 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Estadísticas y Caja | 183 × 36 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Utilidades Android | 182 × 36 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Configuración de taller | 214 × 36 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Detectar equipos | 172 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Reiniciar ADB | 146 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Escanear aplicaciones | 207 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | ¿Qué app está en pantalla? | 245 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Marcar sospechosas | 194 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Desmarcar todo | 163 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Bloquear anuncios flotantes | 252 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Limpiar notificaciones spam de Chrome | 335 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Desactivar marcadas | 200 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Desinstalar marcadas | 205 × 32 | Sin recorte de contenido |
| Utilidades Android/Remoción de Malware | Limpiar registro | 164 × 32 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Órdenes de trabajo | 187 × 36 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Nueva orden | 139 × 36 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Inventario | 121 × 36 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Catálogo y Ubicaciones | 216 × 36 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Estadísticas y Caja | 183 × 36 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Utilidades Android | 182 × 36 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Configuración de taller | 214 × 36 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Detectar equipos | 172 × 32 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Reiniciar ADB | 146 × 32 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Leer DNS actual | 164 × 32 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Anclar DNS en el equipo | 223 × 32 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Probar conexión DNS | 201 × 32 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Restaurar DNS automático | 241 × 32 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Desactivar DNS privado | 220 × 32 | Sin recorte de contenido |
| Utilidades Android/Anclar DNS | Limpiar registro | 164 × 32 | Sin recorte de contenido |
| Configuración de taller | Órdenes de trabajo | 187 × 36 | Sin recorte de contenido |
| Configuración de taller | Nueva orden | 139 × 36 | Sin recorte de contenido |
| Configuración de taller | Inventario | 121 × 36 | Sin recorte de contenido |
| Configuración de taller | Catálogo y Ubicaciones | 216 × 36 | Sin recorte de contenido |
| Configuración de taller | Estadísticas y Caja | 183 × 36 | Sin recorte de contenido |
| Configuración de taller | Utilidades Android | 182 × 36 | Sin recorte de contenido |
| Configuración de taller | Configuración de taller | 214 × 36 | Sin recorte de contenido |
| Configuración de taller | Probar impresión | 173 × 32 | Sin recorte de contenido |
| Configuración de taller | Cambiar tema visual | 50 × 36 | Sin recorte de contenido |
| Configuración de taller | Elegir logo | 124 × 32 | Sin recorte de contenido |
| Configuración de taller | Insertar texto de ejemplo | 233 × 32 | Sin recorte de contenido |
| Configuración de taller | Guardar Configuración | 211 × 32 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Órdenes de trabajo | 187 × 36 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Nueva orden | 139 × 36 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Inventario | 121 × 36 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Catálogo y Ubicaciones | 216 × 36 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Estadísticas y Caja | 183 × 36 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Utilidades Android | 182 × 36 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Configuración de taller | 214 × 36 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Bloquear edición | 196 × 32 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Agregar producto | 176 × 32 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Restar 1 al stock | 44 × 32 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Sumar 1 al stock | 44 × 32 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Editar | 88 × 32 | Sin recorte de contenido |
| Inventario/edición desbloqueada | Eliminar | 104 × 32 | Sin recorte de contenido |
| Diálogo/Editar orden #0001 | Cancelar | 110 × 32 | Sin recorte de contenido |
| Diálogo/Editar orden #0001 | Guardar cambios | 170 × 32 | Sin recorte de contenido |
| Diálogo/Editar servicio | Cancelar | 110 × 32 | Sin recorte de contenido |
| Diálogo/Editar servicio | Guardar cambios | 170 × 32 | Sin recorte de contenido |
| Diálogo/Editar ubicación | Cancelar | 110 × 32 | Sin recorte de contenido |
| Diálogo/Editar ubicación | Guardar cambios | 170 × 32 | Sin recorte de contenido |
| Diálogo/Agregar producto al inventario | Cancelar | 110 × 32 | Sin recorte de contenido |
| Diálogo/Agregar producto al inventario | Guardar producto | 176 × 32 | Sin recorte de contenido |
| Diálogo/Editar producto | Cancelar | 110 × 32 | Sin recorte de contenido |
| Diálogo/Editar producto | Guardar cambios | 170 × 32 | Sin recorte de contenido |
| Diálogo/Ticket digital — Folio #0001 | Abrir imagen | 141 × 32 | Sin recorte de contenido |
| Diálogo/Ticket digital — Folio #0001 | Abrir carpeta | 143 × 32 | Sin recorte de contenido |
| Diálogo/Ticket digital — Folio #0001 | Enviar por WhatsApp | 201 × 32 | Sin recorte de contenido |
| Diálogo/Ticket digital — Folio #0001 | Cerrar | 92 × 32 | Sin recorte de contenido |
| Diálogo/Captura de pantalla del equipo | Abrir imagen | 141 × 32 | Sin recorte de contenido |
| Diálogo/Captura de pantalla del equipo | Abrir carpeta | 143 × 32 | Sin recorte de contenido |
| Diálogo/Captura de pantalla del equipo | Cerrar | 92 × 32 | Sin recorte de contenido |
| Diálogo/Modo maestro | Cerrar | 92 × 32 | Sin recorte de contenido |
| Diálogo/Modo maestro | Borrar todas las órdenes | 227 × 32 | Sin recorte de contenido |
| Diálogo/Modo maestro | Restablecer base de datos completa | 312 × 32 | Sin recorte de contenido |
| Diálogo/Modo maestro | Cambiar código maestro | 225 × 32 | Sin recorte de contenido |
| Diálogo/Mensajes estándar | Aceptar | 83 × 32 | Sin recorte de contenido |
| Diálogo/Mensajes estándar | Sí | 40 × 32 | Sin recorte de contenido |
| Diálogo/Mensajes estándar | No | 44 × 32 | Sin recorte de contenido |
| Diálogo/Código maestro | Aceptar | 83 × 32 | Sin recorte de contenido |
| Diálogo/Código maestro | Cancelar | 89 × 32 | Sin recorte de contenido |
| Diálogo/Archivos Qt | Abrir | 62 × 32 | Sin recorte de contenido |
| Diálogo/Archivos Qt | Cancelar | 89 × 32 | Sin recorte de contenido |

## Retirados

- Elegir adb.exe
- ¿Cómo conectar por USB?
- Refrescar datos

## Incidencias

Ninguna incidencia geométrica de botones en las condiciones probadas.
