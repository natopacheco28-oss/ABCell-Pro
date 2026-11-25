# ABCell Tizimin — Taller

Sistema de gestión de taller de celulares y otros equipos, escrito en **Python y PySide6 (Qt 6)**. Incluye órdenes, pagos, inventario, catálogo, ubicaciones, reportes, tickets y utilidades Android ADB.

## Ejecutar desde el código completo

Recomendado: Python 3.12 en Windows 10/11.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

En Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

Qt requiere bibliotecas gráficas del sistema. En Debian/Ubuntu, para pruebas sin pantalla:

```bash
sudo apt-get install libgl1 libegl1 libxkbcommon0 libdbus-1-3
QT_QPA_PLATFORM=offscreen .venv/bin/python tools/audit_ui.py
```

Para una sesión gráfica Linux también se necesitan las dependencias de la plataforma X11/Wayland de Qt que correspondan al escritorio. La impresión de tickets con `pywin32` está diseñada para Windows.

## Rediseño global

- Identidad oscura **Lima Pro** en todas las vistas y diálogos Qt.
- Fondo `#0c111b`, tarjetas `#151e2c`, texto `#edf2f7` y acento `#c5f467`.
- Escaneo/detección en ámbar; acciones destructivas/desactivar en rojo oscuro.
- Seis variantes oscuras. Las preferencias antiguas se traducen a nombres compatibles sin modificar órdenes, pagos ni inventario.
- Botones calculados por texto, icono y padding: al menos **44 px lógicos**; navegación **48 px**.
- Filas adaptables: los controles completos pasan a una nueva línea. Cada etiqueta de filtro permanece con su campo.
- Formularios con ajuste de filas; notas y falla multilinea; tarjetas y descripciones con word-wrap.
- Scroll accesible cuando el contenido supera el tamaño disponible; no se reduce la tipografía ni se aplastan botones.
- Tablas con texto sin elipsis, filas ajustables y columnas que reservan espacio para sus acciones. Scroll horizontal para columnas fuera del viewport.
- Diálogos largos con formulario desplazable y acciones finales visibles. Selectores de archivos Qt para mantener el mismo estilo.
- Eliminados: **Elegir adb.exe**, **¿Cómo conectar por USB?**, **Refrescar datos**. ADB conserva su búsqueda automática. Los datos siguen actualizándose al navegar y guardar.

La interfaz conserva la lógica de negocio y las integraciones existentes. No es una maqueta ni un conjunto de fragmentos.

## Estructura del código

| Archivo / carpeta | Responsabilidad |
|---|---|
| `main.py` | Arranque y carpeta de datos portable |
| `config/settings.py`, `config/assets.py` | Preferencias, seguridad e identidad |
| `core/catalog_data.py` | Categorías, estados y métodos de pago |
| `database/db_manager.py` | SQLite, migraciones y respaldos |
| `services/workshop_service.py` | Órdenes, pagos, catálogo, ubicaciones e inventario |
| `integrations/printer_58mm.py` | Tickets e impresión térmica Windows |
| `integrations/ticket_image.py` | Ticket digital PNG |
| `integrations/whatsapp_center.py` | Mensajes y enlaces WhatsApp |
| `integrations/adb_manager.py` | Diagnóstico y utilidades ADB |
| `ui/main_window.py` | Todas las pantallas y diálogos del taller |
| `ui/theme.py` | QSS global, paletas y gestor de temas |
| `ui/layouts.py` | Controles seguros, filas adaptables, tablas y diálogos |
| `ui/icons.py`, `ui/assets/` | Iconos vectoriales HiDPI y recursos |
| `tests/` | Pruebas de negocio y regresión de distribución |
| `tools/audit_ui.py` | Inventario y verificación de botones con capturas |
| `.github/workflows/` | Compilación Windows y verificaciones de interfaz |

## Datos y actualización

`data/` contiene la base SQLite y la configuración. En el ejecutable portable vive junto al `.exe`; conserva **toda la carpeta** al mover el programa. Las versiones anteriores que usaban `%LOCALAPPDATA%\ABCell_Gestion_Taller` se copian al nuevo destino si no existen ya archivos en él. La carpeta `respaldos/` se utiliza para las copias de seguridad.

**Antes de actualizar una instalación real, cierra el programa y respalda `data/` y la ubicación antigua, si existe.** El paquete de código no incluye datos ni contraseñas reales.

## Pruebas y verificación botón por botón

```bash
python -m compileall -q config core database integrations services ui tools tests main.py
python -m unittest discover -s tests -v
python tools/audit_ui.py --output artifacts/ui
```

La última orden utiliza Qt offscreen por defecto, datos temporales y simulación de la captura ADB; no imprime, no se conecta a teléfonos y no ejecuta acciones destructivas.

Genera:

- `BUTTON_CHECKLIST.md`: pantalla, nombre de cada botón, medidas mínimas y resultado.
- `buttons.json`: dimensiones reales en cada resolución, cobertura e incidencias.
- Capturas PNG de las vistas y diálogos.

La auditoría recorre 900×600, 1366×768 y 1920×1080 y falla si un botón no contiene sus glifos/iconos, invade a otro, sobresale de su contenedor o no fue cubierto según el código fuente. El workflow repite las pruebas a escalas de 100 %, 150 % y 200 %.

Consulta [la verificación completa de botones](docs/VERIFICACION_BOTONES.md) y [las notas del rediseño](docs/REDISENO.md). La comprobación geométrica no equivale a probar impresoras o dispositivos físicos ni certifica todo posible texto introducido por el usuario.

## Compilar el ejecutable Windows

También puedes compilar localmente desde PowerShell:

```powershell
.\tools\build_windows.ps1
```

El script crea el entorno, instala dependencias, verifica botones y empaqueta ADB. Si no encuentra platform-tools, lo descarga desde Google. Usa `-SkipAdbDownload` para exigir una instalación local de ADB.

En GitHub Actions, ejecuta **Compilar ABCell Pro .exe** sobre la rama que quieras compilar. El workflow comprueba el código, ejecuta las pruebas y la auditoría Qt en Windows, prepara ADB y genera con PyInstaller:

```text
ABCell_Gestion_Taller.exe
```

Se publica como artefacto **ABCell_Gestion_Taller_exe**, acompañado de **verificacion-ui-windows**. El `.exe` Windows debe compilarse en Windows: no es una compilación cruzada desde Linux.
