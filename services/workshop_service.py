try:
    from services.workshop_service import WorkshopService
except Exception:
    class WorkshopService:  # type: ignore
        def __init__(self, db, config):
            self.db = db
            self.config = config

        def listar_ordenes(self, *args, **kwargs):
            return []

        def listar_clientes(self, *args, **kwargs):
            return []

        def listar_servicios(self, *args, **kwargs):
            return []

        def listar_ubicaciones(self, *args, **kwargs):
            return []

        def obtener_metricas_dashboard(self, *args, **kwargs):
            return {
                "activas": 0,
                "por_entregar": 0,
                "guardados_7": 0,
                "anticipos_totales": 0.0,
                "saldos_pendientes": 0.0,
                "lista_por_entregar": [],
                "actividad_reciente": [],
            }

        def generar_reporte_financiero(self, *args, **kwargs):
            return {
                "ingresos_diarios": 0.0,
                "ingresos_mensuales": 0.0,
                "saldos_pendientes": 0.0,
                "ganancia_neta_mes": 0.0,
                "por_categoria": {},
            }

        def crear_orden(self, datos):
            return 1

        def obtener_orden(self, folio):
            return None

        def registrar_pago(self, *args, **kwargs):
            return None

        def actualizar_orden_detalle(self, *args, **kwargs):
            return None

        def guardar_servicio(self, *args, **kwargs):
            return 1

        def guardar_ubicacion(self, *args, **kwargs):
            return None


try:
    from integrations.whatsapp_center import WhatsAppCenter
except Exception:
    class WhatsAppCenter:  # type: ignore
        def __init__(self, db, config):
            self.db = db
            self.config = config

        def construir_mensaje(self, tipo, orden):
            return ""

        def generar_url_wa(self, telefono, mensaje):
            return "https://wa.me/"

        def registrar_notificacion(self, *args, **kwargs):
            return None

        def listar_notificaciones(self, *args, **kwargs):
            return []
