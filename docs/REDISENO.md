# Rediseño global — ABCell Pro

## Implementación completa

El rediseño está aplicado al sistema existente en Python/PySide6. No se sustituyó por una maqueta ni se eliminaron los métodos de negocio. Las únicas acciones retiradas de la interfaz son las tres solicitadas y sus dos callbacks ADB ya sin uso.

### Cobertura de pantallas

| Área | Distribución y componentes |
|---|---|
| Órdenes de trabajo | Etapas, filtros con etiqueta inseparable, tabla, estado, ubicación, edición, abono, métodos de pago, impresión, ticket digital y eliminación |
| Nueva orden | Datos de orden, cliente, equipo, servicio rápido y falla, ubicación, clave/patrón, importes y notas, limpieza y guardado |
| Inventario | Resumen, búsqueda, filtros, protección de edición, alta/edición de producto, ajustes de stock y eliminación |
| Catálogo y Ubicaciones | Formularios adaptables, tablas con acciones dimensionadas, diálogos de edición y confirmaciones |
| Estadísticas y Caja | Métricas y tabla de reportes con la misma identidad |
| Utilidades Android | Conexión automática, diagnóstico, malware, DNS y registro de actividad con scroll |
| Configuración | Identidad, contacto, impresora, temas, logo, garantía y guardado |
| Secundarias | Ticket digital, captura ADB, modo maestro, código maestro, mensajes y selectores de archivos Qt |

### Archivos de presentación

- `ui/theme.py`: estilos completos para widgets, estados de foco/hover/deshabilitado, tablas, menús, pestañas, scrollbars y diálogos; seis paletas oscuras compatibles con preferencias anteriores.
- `ui/layouts.py`:
  - `ActionButton`: caja de contenido calculada según fuente, icono y padding; 32 px lógicos como mínimo.
  - `FlowLayout`: distribución con saltos de línea y soporte de sublayouts/campos expansibles.
  - `ContentCombo`: mantiene un ancho compacto y conserva el texto completo en el desplegable y tooltip.
  - `MultilineInput`: descripciones con word-wrap y API compatible con los formularios.
  - `ReadableTable`: filas dimensionadas por contenido y columnas distribuidas según el viewport, preservando el ancho mínimo de las acciones.
  - `AdaptiveDialog`: formulario desplazable y acciones finales fuera del scroll.
  - `VisualPolicy`: reglas comunes también para botones de Qt y formularios de diálogos; paleta oscura, estilo Fusion, traducciones españolas y retirada segura del filtro al cerrar.
  - `scroll_page`: conserva el acceso al contenido cuando no cabe en el viewport.
- `ui/main_window.py`: todas las vistas reales, agrupación de nueva orden, eliminación de botones y uso de los controles anteriores.
- `ui/icons.py`: SVG con color aplicado realmente al trazo y resolución HiDPI.
- `ui/assets/chevron-down.svg`: indicador legible de desplegables, empaquetado junto al programa.

## Reglas anti-recorte

1. No se establecen alturas máximas de 26/30 px para botones con texto.
2. El ancho se calcula con `QFontMetrics`, sin estimarlo por número de caracteres.
3. Las filas adaptables envuelven controles completos; los mínimos no se sacrifican para forzar una sola fila.
4. Los labels descriptivos usan word-wrap y los formularios `WrapLongRows`.
5. Los campos internos de combos/spinboxes no reciben la altura mínima exterior ni padding duplicado.
6. Las tablas cuentan el padding QSS al dimensionar sus celdas de acciones.
7. El menú lateral no tiene un máximo rígido que pueda quedar por debajo de la fuente de Windows.
8. El viewport puede desplazarse; **scroll no significa truncamiento del contenido**. Los textos editables también conservan su desplazamiento normal.
9. Los diálogos de edición mantienen acciones finales visibles y limitan su tamaño al monitor.
10. La tipografía no tiene sombras, animaciones ni efectos que reduzcan la legibilidad.

## Verificación reproducible

`tools/audit_ui.py` crea datos temporales y recorre todas las vistas y los diálogos. No opera con la base real, no imprime, no realiza operaciones ADB sobre teléfonos y no pulsa acciones destructivas.

Comprueba para cada botón:

- Dimensiones reales frente a glifos/icono/padding calculados.
- Contención dentro del widget padre.
- Ausencia de superposición con otro botón del mismo padre.
- Cobertura contra los nombres de las acciones en el AST del código fuente.
- Ausencia de los tres botones retirados.

Incluye estados bloqueado/desbloqueado del inventario y acciones de filas creadas con datos de prueba. Las capturas ADB se simulan únicamente para construir su diálogo.

### Evidencia de CI de la revisión compacta

- Linux/Qt offscreen, commit `e880772`: 20 pruebas aprobadas, incluida la regresión de catálogo a 1358×690, y 168 combinaciones botón/sección sin incidencias a escalas 100 %, 150 % y 200 %.
- [Ejecución de comprobación](https://github.com/natopacheco28-oss/ABCell-Pro/actions/runs/45660881877).
- Resoluciones de auditoría: 900×600, 1358×690, 1366×768 y 1920×1080.
- Los informes repiten la navegación en cada sección; el total no representa nombres únicos.
- Windows nativo, mismo commit: 20 pruebas aprobadas, 168 combinaciones sin incidencias y compilación PyInstaller completada. [Ejecución y artefacto ABCell-Pro-Windows](https://github.com/natopacheco28-oss/ABCell-Pro/actions/runs/45660882829).
- El backend genérico offscreen en Windows produjo métricas de fuente incorrectas en CI; las pruebas Windows ahora usan su plataforma nativa, igual que el programa instalado.
- El ejecutable generado es `ABCell Pro.exe`, con el ICO multirresolución derivado del logo suministrado y metadatos de producto ABCell Pro. No se ha probado interactivamente el ejecutable empaquetado ni hardware físico.

Consulta [VERIFICACION_BOTONES.md](VERIFICACION_BOTONES.md) para la lista completa con medidas.

## Límites de la comprobación

Una auditoría geométrica no certifica todos los posibles datos libres, fuentes instaladas, configuraciones de accesibilidad o tamaños de monitor. La interfaz ofrece word-wrap, dimensiones basadas en contenido y scroll para esos casos. Las pruebas sin pantalla no sustituyen la revisión visual interactiva final en el equipo de destino.

Las impresoras de 58/80 mm, un Android físico y sus permisos/drivers requieren una prueba de hardware. El formato de los tickets en papel sigue siendo claro para no gastar tinta; el fondo oscuro pertenece a la interfaz de la aplicación.
