# ABCell Pro Demo — prueba sin internet

Edición independiente y reducida, con la identidad oscura/lima y el icono de ABCell Pro. No es el programa completo con botones ocultos. No requiere cuenta, servidor, dominio, suscripción ni conexión a internet para utilizarla.

## Uso para el negocio que recibe la demo

Descomprime **ABCell-Pro-Demo-Windows.zip** en una carpeta y abre **ABCell Pro Demo.exe**. No requiere instalar Python. No distribuyas el ZIP de código fuente como si fuera el ejecutable.

- La primera apertura inicia **168 horas (7 días naturales)** según el reloj de esa PC. Descargar, copiar o descomprimir el ZIP no inicia el plazo. El tiempo sigue transcurriendo con el programa cerrado.
- Incluye alta y consulta de **hasta 20 órdenes**, búsqueda, importes y configuración básica del taller.
- **No incluye** impresión, tickets digitales, exportación, edición/borrado de órdenes, abonos, inventario, catálogo, caja/reportes, utilidades ADB ni modo maestro. Estos módulos de la versión completa no se empaquetan en esta edición. No hay botón o clave para desbloquearlos.
- Vencimiento o atraso importante del reloj: se bloquea el acceso y se conserva la base local; no se eliminan datos. La revisión se hace al abrir, en cada operación y cada 30 segundos mientras está abierta. Se toleran ajustes pequeños del reloj (5 minutos).
- El plazo corresponde al **perfil de usuario del sistema**, no garantiza un plazo por PC física. Descomprimir otra vez o mover el ejecutable no lo reinicia en el mismo perfil. Otro usuario, una reinstalación o borrar/manipular todos los registros locales puede eludirlo. La firma de integridad solo detecta cambios casuales: NO es un DRM inviolable. No se promete detectar cualquier alteración del reloj ni de la máquina.
- Utiliza datos ficticios para evaluar. No tiene exportación ni migración automática a la versión completa. No asumas que la base demo es compatible con la base de producción.

## Ubicación de la prueba y datos (sin ocultamientos)

Windows: `%LOCALAPPDATA%\ABCellProDemo\`:

- `trial.json`: primera apertura y última fecha observada, con comprobación de integridad.
- `orders.sqlite3`: órdenes y datos del taller de la demo; nunca se abre la BD de ABCell Pro completo.
- `running.lock`: bloqueo de instancia por perfil.

Respaldo del registro de prueba en Windows: `HKEY_CURRENT_USER\Software\ABCell\ABCellProDemo`, valor `TrialState`. Si se borra una sola copia se repone con la restante, sin reiniciar el plazo. Si hay datos de demo pero faltan ambos registros, se bloquea en lugar de empezar de nuevo.

Linux para desarrollo: `$XDG_DATA_HOME/ABCellProDemo` o `~/.local/share/ABCellProDemo`. Solo tiene el registro de archivo; no usa registro de Windows.

La demo no se registra como servicio ni arranca con Windows; no necesita administrador. No contacta servidores ni envía datos. Los metadatos de autor no constituyen una firma digital Authenticode ni evitan SmartScreen.

## Código y compilación

Recomendado Python 3.12. En el ZIP de código independiente:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
.\build_windows.ps1
```

Resultado: `dist/ABCell Pro Demo.exe`. La compilación Windows se realiza en Windows. La distribución NO debe incluir el código fuente, registros de pruebas, licencias iniciadas ni datos de otro taller.

En el repositorio de desarrollo original también se puede ejecutar `python -m offline_demo.main`; no modifica el arranque de `main.py` de la versión completa.

Pruebas: `python -m unittest discover -s tests -p 'test_demo_*.py' -v`. Los tests usan directorios y registros en memoria temporales, nunca inician la prueba del perfil real. Las pruebas gráficas requieren las bibliotecas Qt del sistema; en Linux se usa la plataforma offscreen.

## Repositorio privado separado

El paquete de código independiente contiene solo los módulos reducidos, estilos/controles compartidos, recursos y workflow de compilación demo. Puede subirse a **ABCell-Pro-Demo** privado cuando el propietario cree el repositorio y habilite el acceso. La conexión disponible al preparar esta edición no permitía crear ese repositorio; no se afirma que ya esté publicado allí.

## Evidencia de esta entrega

Código funcional `cc40558`. [Compilación demo Windows](https://github.com/natopacheco28-oss/ABCell-Pro/actions/runs/45713648604): 2 pruebas de aislamiento del paquete y 16 pruebas del código independiente (reloj, vencimiento, integridad, almacenamiento, límite de órdenes y GUI) aprobadas. PyInstaller generó `ABCell Pro Demo.exe`; no se ha realizado una prueba interactiva del ejecutable empaquetado.

[Regresión del repositorio completo](https://github.com/natopacheco28-oss/ABCell-Pro/actions/runs/45713648626): 46 pruebas aprobadas en Linux/Qt offscreen al 100 %, 150 % y 200 %, además de la auditoría de 168 combinaciones botón/sección de la aplicación completa sin incidencias. Estas verificaciones no certifican toda posible fuente, equipo o manipulación del reloj.

La demo recorre cuatro páginas a 900×600, 1358×690 y 1920×1080. Comprueba dimensiones de botones frente a glifos/iconos y contención en su padre. Alta, búsqueda y guardado de configuración tienen pruebas de funcionamiento; las entradas de módulos no incluidos permanecen deshabilitadas y no tienen implementación detrás. Las capturas de Windows se han inspeccionado para la vista de órdenes.

### Lista de botones de la demo


Geometría, no validación de hardware. Páginas: 0 órdenes, 1 nueva, 2 configuración, 3 límites.

| Página | Botón | Mínimo ancho × alto | Resultado |
|---|---|---|---|
| 0 | Catálogo y Ubicaciones | 164 × 32 | Sin recorte geométrico |
| 0 | Configuración de taller | 184 × 32 | Sin recorte geométrico |
| 0 | Estadísticas y Caja | 133 × 32 | Sin recorte geométrico |
| 0 | Inventario | 86 × 32 | Sin recorte geométrico |
| 0 | Nueva orden | 125 × 32 | Sin recorte geométrico |
| 0 | Sobre la demo | 134 × 32 | Sin recorte geométrico |
| 0 | Utilidades Android | 136 × 32 | Sin recorte geométrico |
| 0 | Órdenes de trabajo | 163 × 32 | Sin recorte geométrico |
| 1 | Catálogo y Ubicaciones | 164 × 32 | Sin recorte geométrico |
| 1 | Configuración de taller | 184 × 32 | Sin recorte geométrico |
| 1 | Estadísticas y Caja | 133 × 32 | Sin recorte geométrico |
| 1 | Guardar orden | 135 × 32 | Sin recorte geométrico |
| 1 | Inventario | 86 × 32 | Sin recorte geométrico |
| 1 | Limpiar | 68 × 32 | Sin recorte geométrico |
| 1 | Nueva orden | 125 × 32 | Sin recorte geométrico |
| 1 | Sobre la demo | 134 × 32 | Sin recorte geométrico |
| 1 | Utilidades Android | 136 × 32 | Sin recorte geométrico |
| 1 | Órdenes de trabajo | 163 × 32 | Sin recorte geométrico |
| 2 | Catálogo y Ubicaciones | 164 × 32 | Sin recorte geométrico |
| 2 | Configuración de taller | 184 × 32 | Sin recorte geométrico |
| 2 | Estadísticas y Caja | 133 × 32 | Sin recorte geométrico |
| 2 | Guardar Configuración | 184 × 32 | Sin recorte geométrico |
| 2 | Inventario | 86 × 32 | Sin recorte geométrico |
| 2 | Nueva orden | 125 × 32 | Sin recorte geométrico |
| 2 | Sobre la demo | 134 × 32 | Sin recorte geométrico |
| 2 | Utilidades Android | 136 × 32 | Sin recorte geométrico |
| 2 | Órdenes de trabajo | 163 × 32 | Sin recorte geométrico |
| 3 | Catálogo y Ubicaciones | 164 × 32 | Sin recorte geométrico |
| 3 | Configuración de taller | 184 × 32 | Sin recorte geométrico |
| 3 | Estadísticas y Caja | 133 × 32 | Sin recorte geométrico |
| 3 | Inventario | 86 × 32 | Sin recorte geométrico |
| 3 | Nueva orden | 125 × 32 | Sin recorte geométrico |
| 3 | Sobre la demo | 134 × 32 | Sin recorte geométrico |
| 3 | Utilidades Android | 136 × 32 | Sin recorte geométrico |
| 3 | Órdenes de trabajo | 163 × 32 | Sin recorte geométrico |
