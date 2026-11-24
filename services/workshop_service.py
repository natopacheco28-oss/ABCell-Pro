from datetime import datetime
from config.settings import ConfigManager
from database.db_manager import DatabaseManager


class WorkshopService:
    def __init__(self, db: DatabaseManager, config: ConfigManager):
        self.db = db
        self.config = config

    def _ahora_str(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def crear_orden(self, datos: dict) -> int:
        ahora = self._ahora_str()
        costo_rep = float(datos.get("costo_repuesto") or 0.0)
        costo_total = float(datos.get("costo_total") or 0.0)
        anticipo = float(datos.get("anticipo") or 0.0)
        saldo = max(0.0, costo_total - anticipo)
        metodo_pago = str(datos.get("metodo_pago") or "Efectivo").strip()

        cur = self.db.ejecutar(
            """
            INSERT INTO ordenes (
                cliente_nombre, cliente_tel, categoria, marca, modelo, color,
                imei, pin_pass, patron, estado_fisico, falla, servicio_nombre,
                ubicacion, estatus, costo_repuesto, costo_total, anticipo,
                saldo, metodo_pago, notas_internas, fecha_ingreso, fecha_actualizacion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(datos.get("cliente_nombre") or "").strip(),
                str(datos.get("cliente_tel") or "").strip(),
                str(datos.get("categoria") or "Celulares").strip(),
                str(datos.get("marca") or "").strip(),
                str(datos.get("modelo") or "").strip(),
                str(datos.get("color") or "").strip(),
                str(datos.get("imei") or "").strip(),
                str(datos.get("pin_pass") or "").strip(),
                str(datos.get("patron") or "Sin patrón").strip(),
                str(datos.get("estado_fisico") or "").strip(),
                str(datos.get("falla") or "").strip(),
                str(datos.get("servicio_nombre") or "").strip(),
                str(datos.get("ubicacion") or "Sin asignar").strip(),
                "Recibido",
                costo_rep,
                costo_total,
                anticipo,
                saldo,
                metodo_pago,
                str(datos.get("notas_internas") or "").strip(),
                ahora,
                ahora,
            ),
        )
        folio = int(cur.lastrowid)

        if anticipo > 0:
            self.db.ejecutar(
                """
                INSERT INTO pagos_orden (folio, monto, metodo_pago, fecha)
                VALUES (?, ?, ?, ?)
                """,
                (folio, anticipo, metodo_pago, ahora),
            )

        return folio

    def obtener_orden(self, folio: int) -> dict | None:
        fila = self.db.consultar_uno("SELECT * FROM ordenes WHERE folio = ?", (int(folio),))
        if not fila:
            return None

        try:
            f_ing = datetime.strptime(fila["fecha_ingreso"][:19], "%Y-%m-%d %H:%M:%S")
            dias_espera = max(0, (datetime.now() - f_ing).days)
        except Exception:
            dias_espera = 0

        fila["dias_espera"] = dias_espera
        return fila

    def listar_ordenes(
        self,
        busqueda: str = "",
        estatus: str = "Todos",
        categoria: str = "Todas",
    ) -> list[dict]:
        sql = "SELECT * FROM ordenes WHERE 1=1"
        params: list = []

        if estatus and estatus != "Todos":
            sql += " AND estatus = ?"
            params.append(estatus)

        if categoria and categoria != "Todas":
            sql += " AND categoria = ?"
            params.append(categoria)

        if busqueda and busqueda.strip():
            termino = f"%{busqueda.strip()}%"
            sql += """
                AND (
                    CAST(folio AS TEXT) LIKE ?
                    OR cliente_nombre LIKE ?
                    OR cliente_tel LIKE ?
                    OR marca LIKE ?
                    OR modelo LIKE ?
                    OR falla LIKE ?
                    OR ubicacion LIKE ?
                )
            """
            params.extend([termino] * 7)

        sql += " ORDER BY folio DESC"
        return self.db.consultar_todos(sql, tuple(params))

    def registrar_pago(self, folio: int, monto: float, metodo_pago: str = "Efectivo"):
        orden = self.obtener_orden(folio)
        if not orden:
            return None

        monto = max(0.0, float(monto))
        ahora = self._ahora_str()
        nuevo_anticipo = float(orden.get("anticipo") or 0.0) + monto
        nuevo_saldo = max(0.0, float(orden.get("costo_total") or 0.0) - nuevo_anticipo)

        self.db.ejecutar(
            """
            INSERT INTO pagos_orden (folio, monto, metodo_pago, fecha)
            VALUES (?, ?, ?, ?)
            """,
            (int(folio), monto, metodo_pago, ahora),
        )
        self.db.ejecutar(
            """
            UPDATE ordenes
            SET anticipo = ?, saldo = ?, metodo_pago = ?, fecha_actualizacion = ?
            WHERE folio = ?
            """,
            (nuevo_anticipo, nuevo_saldo, metodo_pago, ahora, int(folio)),
        )
        return self.obtener_orden(folio)

    def actualizar_orden_detalle(
        self,
        folio: int,
        estatus: str,
        ubicacion: str,
        notas_internas: str = "",
        liquidar_al_entregar: bool = True,
        metodo_pago_entrega: str = "Efectivo",
    ):
        orden = self.obtener_orden(folio)
        if not orden:
            return None

        ahora = self._ahora_str()
        nuevo_anticipo = float(orden.get("anticipo") or 0.0)
        nuevo_saldo = float(orden.get("saldo") or 0.0)

        if estatus == "Entregado" and liquidar_al_entregar and nuevo_saldo > 0:
            self.db.ejecutar(
                """
                INSERT INTO pagos_orden (folio, monto, metodo_pago, fecha)
                VALUES (?, ?, ?, ?)
                """,
                (int(folio), nuevo_saldo, metodo_pago_entrega, ahora),
            )
            nuevo_anticipo = float(orden.get("costo_total") or 0.0)
            nuevo_saldo = 0.0

        self.db.ejecutar(
            """
            UPDATE ordenes
            SET estatus = ?, ubicacion = ?, notas_internas = ?,
                anticipo = ?, saldo = ?, fecha_actualizacion = ?
            WHERE folio = ?
            """,
            (
                estatus,
                ubicacion,
                notas_internas,
                nuevo_anticipo,
                nuevo_saldo,
                ahora,
                int(folio),
            ),
        )
        return self.obtener_orden(folio)

    def eliminar_orden(self, folio: int) -> bool:
        folio = int(folio)
        existe = self.db.consultar_uno(
            "SELECT folio FROM ordenes WHERE folio = ?", (folio,)
        )
        if not existe:
            return False
        self.db.ejecutar("DELETE FROM pagos_orden WHERE folio = ?", (folio,))
        self.db.ejecutar(
            "DELETE FROM notificaciones_wa WHERE folio = ?", (folio,)
        )
        self.db.ejecutar("DELETE FROM ordenes WHERE folio = ?", (folio,))
        return True

    def obtener_metricas_dashboard(self, categoria: str = "Todas") -> dict:
        ordenes = self.listar_ordenes(categoria=categoria)
        cerrados = {"Entregado", "Cancelado"}

        activas_lista = [o for o in ordenes if o.get("estatus") not in cerrados]
        por_entregar_lista = [o for o in ordenes if o.get("estatus") == "Listo para entregar"]

        guardados_7 = 0
        for o in activas_lista:
            try:
                f_ing = datetime.strptime(o["fecha_ingreso"][:19], "%Y-%m-%d %H:%M:%S")
                if (datetime.now() - f_ing).days >= 7:
                    guardados_7 += 1
            except Exception:
                pass

        anticipos_totales = sum(float(o.get("anticipo") or 0.0) for o in ordenes)
        saldos_pendientes = sum(float(o.get("saldo") or 0.0) for o in activas_lista)

        return {
            "activas": len(activas_lista),
            "por_entregar": len(por_entregar_lista),
            "guardados_7": guardados_7,
            "anticipos_totales": anticipos_totales,
            "saldos_pendientes": saldos_pendientes,
            "lista_por_entregar": por_entregar_lista[:15],
            "actividad_reciente": ordenes[:15],
        }

    def listar_clientes(self, busqueda: str = "") -> list[dict]:
        ordenes = self.listar_ordenes()
        agrupado: dict[str, dict] = {}

        for o in ordenes:
            nombre = str(o.get("cliente_nombre") or "").strip()
            tel = str(o.get("cliente_tel") or "").strip()
            clave = f"{nombre.lower()}|{tel}"

            if clave not in agrupado:
                agrupado[clave] = {
                    "id": len(agrupado) + 1,
                    "nombre": nombre,
                    "telefono": tel,
                    "total_ordenes": 0,
                    "total_facturado": 0.0,
                    "saldo_pendiente": 0.0,
                }

            agrupado[clave]["total_ordenes"] += 1
            agrupado[clave]["total_facturado"] += float(o.get("costo_total") or 0.0)
            if o.get("estatus") not in ("Entregado", "Cancelado"):
                agrupado[clave]["saldo_pendiente"] += float(o.get("saldo") or 0.0)

        clientes = list(agrupado.values())
        if busqueda and busqueda.strip():
            q = busqueda.strip().lower()
            clientes = [
                c
                for c in clientes
                if q in c["nombre"].lower() or q in c["telefono"].lower()
            ]
        return clientes

    def listar_servicios(self, solo_activos: bool = False) -> list[dict]:
        if solo_activos:
            return self.db.consultar_todos(
                "SELECT * FROM servicios_catalogo WHERE COALESCE(activo, 1) = 1 ORDER BY id DESC"
            )
        return self.db.consultar_todos("SELECT * FROM servicios_catalogo ORDER BY id DESC")

    def guardar_servicio(self, datos: dict) -> int:
        cur = self.db.ejecutar(
            """
            INSERT INTO servicios_catalogo (categoria, marca, modelo, nombre, precio, activo)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(datos.get("categoria") or "Celulares").strip(),
                str(datos.get("marca") or "").strip(),
                str(datos.get("modelo") or "").strip(),
                str(datos.get("nombre") or "").strip(),
                float(datos.get("precio") or 0.0),
                1 if datos.get("activo", True) else 0,
            ),
        )
        return int(cur.lastrowid)

    def listar_ubicaciones(self, solo_activas: bool = True) -> list[dict]:
        if solo_activas:
            return self.db.consultar_todos(
                "SELECT * FROM ubicaciones WHERE COALESCE(activo, 1) = 1 ORDER BY id ASC"
            )
        return self.db.consultar_todos("SELECT * FROM ubicaciones ORDER BY id ASC")

    def guardar_ubicacion(self, nombre: str, tipo: str = "General", descripcion: str = ""):
        nombre_limpio = str(nombre or "").strip()
        if not nombre_limpio:
            return None
        self.db.ejecutar(
            """
            INSERT OR IGNORE INTO ubicaciones (nombre, tipo, descripcion, activo)
            VALUES (?, ?, ?, 1)
            """,
            (nombre_limpio, str(tipo or "General").strip(), str(descripcion or "").strip()),
        )
        return nombre_limpio

    def actualizar_servicio(self, servicio_id: int, datos: dict) -> bool:
        """Actualiza un servicio del catálogo. Devuelve False si no existe."""
        servicio_id = int(servicio_id)
        existe = self.db.consultar_uno(
            "SELECT id FROM servicios_catalogo WHERE id = ?", (servicio_id,)
        )
        if not existe:
            return False
        self.db.ejecutar(
            """
            UPDATE servicios_catalogo
            SET categoria = ?, marca = ?, modelo = ?, nombre = ?, precio = ?
            WHERE id = ?
            """,
            (
                str(datos.get("categoria") or "Celulares").strip(),
                str(datos.get("marca") or "").strip(),
                str(datos.get("modelo") or "").strip(),
                str(datos.get("nombre") or "").strip(),
                float(datos.get("precio") or 0.0),
                servicio_id,
            ),
        )
        return True

    def eliminar_servicio(self, servicio_id: int) -> bool:
        """Elimina un servicio del catálogo. Devuelve False si no existe."""
        servicio_id = int(servicio_id)
        existe = self.db.consultar_uno(
            "SELECT id FROM servicios_catalogo WHERE id = ?", (servicio_id,)
        )
        if not existe:
            return False
        self.db.ejecutar("DELETE FROM servicios_catalogo WHERE id = ?", (servicio_id,))
        return True

    def actualizar_ubicacion(
        self, ubicacion_id: int, nombre: str, tipo: str = "General", descripcion: str = ""
    ) -> bool:
        """Actualiza una ubicación. Devuelve False si no existe o el nombre ya está en uso."""
        ubicacion_id = int(ubicacion_id)
        nombre_limpio = str(nombre or "").strip()
        if not nombre_limpio:
            return False
        existe = self.db.consultar_uno(
            "SELECT id FROM ubicaciones WHERE id = ?", (ubicacion_id,)
        )
        if not existe:
            return False
        duplicada = self.db.consultar_uno(
            "SELECT id FROM ubicaciones WHERE nombre = ? AND id != ?",
            (nombre_limpio, ubicacion_id),
        )
        if duplicada:
            return False
        self.db.ejecutar(
            """
            UPDATE ubicaciones
            SET nombre = ?, tipo = ?, descripcion = ?
            WHERE id = ?
            """,
            (
                nombre_limpio,
                str(tipo or "General").strip(),
                str(descripcion or "").strip(),
                ubicacion_id,
            ),
        )
        return True

    def eliminar_ubicacion(self, ubicacion_id: int) -> bool:
        """Elimina una ubicación. Devuelve False si no existe."""
        ubicacion_id = int(ubicacion_id)
        existe = self.db.consultar_uno(
            "SELECT id FROM ubicaciones WHERE id = ?", (ubicacion_id,)
        )
        if not existe:
            return False
        self.db.ejecutar("DELETE FROM ubicaciones WHERE id = ?", (ubicacion_id,))
        return True

    def generar_reporte_financiero(self) -> dict:
        hoy_str = datetime.now().strftime("%Y-%m-%d")
        mes_str = datetime.now().strftime("%Y-%m")

        pagos = self.db.consultar_todos("SELECT * FROM pagos_orden")
        ingresos_diarios = sum(
            float(p.get("monto") or 0.0)
            for p in pagos
            if str(p.get("fecha") or "").startswith(hoy_str)
        )
        ingresos_mensuales = sum(
            float(p.get("monto") or 0.0)
            for p in pagos
            if str(p.get("fecha") or "").startswith(mes_str)
        )

        ordenes = self.listar_ordenes()
        ordenes_mes = [
            o for o in ordenes if str(o.get("fecha_ingreso") or "").startswith(mes_str)
        ]

        facturado_mes = sum(float(o.get("costo_total") or 0.0) for o in ordenes_mes)
        repuestos_mes = sum(float(o.get("costo_repuesto") or 0.0) for o in ordenes_mes)
        ganancia_neta_mes = facturado_mes - repuestos_mes

        saldos_pendientes = sum(
            float(o.get("saldo") or 0.0)
            for o in ordenes
            if o.get("estatus") not in ("Entregado", "Cancelado")
        )

        por_categoria: dict[str, dict] = {}
        for o in ordenes:
            cat = str(o.get("categoria") or "Otros")
            if cat not in por_categoria:
                por_categoria[cat] = {
                    "ordenes": 0,
                    "facturado": 0.0,
                    "costo_rep": 0.0,
                    "ganancia": 0.0,
                }
            fact = float(o.get("costo_total") or 0.0)
            rep = float(o.get("costo_repuesto") or 0.0)
            por_categoria[cat]["ordenes"] += 1
            por_categoria[cat]["facturado"] += fact
            por_categoria[cat]["costo_rep"] += rep
            por_categoria[cat]["ganancia"] += fact - rep

        return {
            "ingresos_diarios": ingresos_diarios,
            "ingresos_mensuales": ingresos_mensuales,
            "saldos_pendientes": saldos_pendientes,
            "ganancia_neta_mes": ganancia_neta_mes,
            "por_categoria": por_categoria,
        }
