import os
import re
import shutil
import subprocess
import sys
from datetime import datetime


PROVEEDORES_DNS = [
    {
        "id": "adguard",
        "nombre": "AdGuard DNS — Bloquea anuncios y pop-ups (Recomendado)",
        "hostname": "dns.adguard-dns.com",
        "descripcion": (
            "Bloquea anuncios en aplicaciones, juegos y páginas web, además de "
            "rastreadores y dominios publicitarios molestos."
        ),
    },
    {
        "id": "adguard_family",
        "nombre": "AdGuard Familiar — Sin anuncios + Protección familiar",
        "hostname": "family.adguard-dns.com",
        "descripcion": (
            "Bloquea anuncios, rastreadores, sitios peligrosos y contenido para adultos, "
            "activando búsqueda segura."
        ),
    },
    {
        "id": "cloudflare_sec",
        "nombre": "Cloudflare Seguridad — Anti-Malware y Anti-Phishing",
        "hostname": "security.cloudflare-dns.com",
        "descripcion": (
            "DNS rápido que bloquea sitios conocidos de malware, virus, troyanos "
            "y páginas falsas de robo de contraseñas."
        ),
    },
    {
        "id": "cloudflare_fam",
        "nombre": "Cloudflare Familiar — Anti-Malware + Control parental",
        "hostname": "family.cloudflare-dns.com",
        "descripcion": (
            "Protege contra malware y phishing, y bloquea sitios con contenido para adultos."
        ),
    },
    {
        "id": "cloudflare",
        "nombre": "Cloudflare 1.1.1.1 — Velocidad y estabilidad",
        "hostname": "one.one.one.one",
        "descripcion": (
            "DNS privado rápido y estable sin bloqueo de contenido. Ideal cuando "
            "el DNS de la compañía telefónica o Wi-Fi falla."
        ),
    },
    {
        "id": "quad9",
        "nombre": "Quad9 — Protección contra amenazas y sitios fraudulentos",
        "hostname": "dns.quad9.net",
        "descripcion": (
            "Bloquea dominios maliciosos, spyware, botnets y enlaces peligrosos."
        ),
    },
    {
        "id": "google",
        "nombre": "Google Public DNS — Estándar compatible",
        "hostname": "dns.google",
        "descripcion": "Servidor DNS global de Google, rápido y de alta compatibilidad.",
    },
    {
        "id": "custom",
        "nombre": "DNS Personalizado (NextDNS / Propio)",
        "hostname": "",
        "descripcion": (
            "Escribe manualmente cualquier servidor DNS sobre TLS (DoT), por ejemplo "
            "abc123.dns.nextdns.io."
        ),
    },
]

MAPA_IP_A_DOT = {
    "1.1.1.1": "one.one.one.one",
    "1.0.0.1": "one.one.one.one",
    "1.1.1.2": "security.cloudflare-dns.com",
    "1.0.0.2": "security.cloudflare-dns.com",
    "1.1.1.3": "family.cloudflare-dns.com",
    "1.0.0.3": "family.cloudflare-dns.com",
    "8.8.8.8": "dns.google",
    "8.8.4.4": "dns.google",
    "9.9.9.9": "dns.quad9.net",
    "149.112.112.112": "dns.quad9.net",
    "94.140.14.14": "dns.adguard-dns.com",
    "94.140.15.15": "dns.adguard-dns.com",
    "94.140.14.15": "family.adguard-dns.com",
    "94.140.15.16": "family.adguard-dns.com",
}

# Paquetes críticos del sistema Android que jamás deben desinstalarse/desactivarse.
PAQUETES_SISTEMA_BLOQUEADOS = {
    "android",
    "com.android.systemui",
    "com.android.settings",
    "com.android.phone",
    "com.android.server.telecom",
    "com.android.providers.settings",
    "com.android.providers.telephony",
    "com.android.providers.contacts",
    "com.android.providers.media",
    "com.android.providers.downloads",
    "com.android.packageinstaller",
    "com.google.android.packageinstaller",
    "com.android.permissioncontroller",
    "com.google.android.permissioncontroller",
    "com.android.vending",
    "com.google.android.gms",
    "com.google.android.gsf",
    "com.android.launcher",
    "com.android.launcher3",
    "com.sec.android.app.launcher",
    "com.miui.home",
    "com.motorola.launcher3",
}

# Apps conocidas y legítimas para evitar falsos positivos en permisos como burbujas/enlaces.
PREFIJOS_APPS_CONFIABLES = (
    "com.whatsapp",
    "com.facebook.",
    "com.instagram.",
    "com.zhiliaoapp.musically",
    "com.ss.android.ugc.trill",
    "org.telegram.messenger",
    "com.spotify.music",
    "com.netflix.mediaclient",
    "com.disney.",
    "com.amazon.",
    "com.mercadolibre",
    "com.mercadopago.",
    "com.bbva.",
    "mx.bancosantander.",
    "com.banorte.",
    "com.citibanamex.",
    "com.nu.production",
    "com.spinbyoxxo",
    "com.paypal.android.",
    "com.microsoft.",
    "com.adobe.",
    "us.zoom.videomeetings",
    "com.ubercab",
    "com.didiglobal.",
    "com.canva.editor",
    "com.duolingo",
    "com.roblox.client",
    "com.dts.freefire",
    "com.activision.",
    "com.supercell.",
    "com.mojang.",
    "com.android.chrome",
    "org.mozilla.firefox",
    "com.brave.browser",
    "com.opera.",
    "com.sec.android.",
    "com.samsung.android.",
    "com.google.android.apps.",
    "com.google.android.youtube",
    "com.google.android.gm",
    "com.google.android.Keep",
    "com.google.android.calendar",
    "com.google.android.calculator",
    "com.google.android.contacts",
    "com.google.android.dialer",
    "com.google.android.inputmethod",
    "com.google.android.tts",
    "com.google.android.webview",
    "com.google.ar.core",
)

PATRONES_ALTO_RIESGO = [
    (r"(^|\.)(junk|ram|phone|virus|super|magic|fancy|nox|keep|hyper|turbo|ultra|max|one|fast|smart|power|master|rocket|ace|zero)[_.]?(clean|cleaner|boost|booster|cooler|antivirus|security)", "Falso limpiador / optimizador con adware"),
    (r"(^|\.)(clean|cleaner|booster|cooler)[_.]?(master|pro|plus|free|lite|max|fast|202\d)", "Limpiador / booster sospechoso de anuncios"),
    (r"(cpu[_.]?cooler|battery[_.]?saver|ram[_.]?booster|junk[_.]?clean|phone[_.]?cooler|fast[_.]?charger)", "Utilidad falsa generadora de publicidad"),
    (r"(pop[_.]?ad|ad[_.]?daemon|float[_.]?ad|lucky[_.]?(spin|wheel|cash|box)|earn[_.]?cash|walk[_.]?earn)", "Módulo conocido de anuncios emergentes"),
    (r"(flashlight|torch|linterna|magnifier|lupa|mirror)[_.]?(pro|free|led|super|bright|plus)", "App linterna/utilidad genérica frecuente en adware"),
    (r"(horoscope|astrology|tarot|palm[_.]?read|wifi[_.]?master|wifi[_.]?key|wifi[_.]?hack)", "App gancho frecuente de spam publicitario"),
]

PATRONES_RIESGO_MEDIO = [
    (r"(clean|cleaner|boost|booster|antivirus|virus|cooler|saver|launcher|theme|wallpaper|ringtone)", "Categoría frecuente de apps con anuncios invasivos"),
    (r"(pdf|qrcode|barcode|scanner|scan|recover|filemanager|files)[_.]?(free|pro|fast|easy|lite|plus|master)", "Utilidad genérica (verificar si muestra anuncios)"),
]

_RE_PAQUETE = re.compile(r"^[A-Za-z0-9._]+$")
_RE_HOSTNAME = re.compile(r"^(?=.{3,253}$)([a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$")
_RE_IPV4 = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")


def normalizar_hostname_dns(valor: str) -> tuple[bool, str, str]:
    """Valida y normaliza un servidor DNS Privado (DoT) para Android 9+.

    Devuelve (es_valido, hostname_limpio, mensaje_aviso).
    """
    limpio = str(valor or "").strip()
    if not limpio:
        return False, "", "Escribe o selecciona un servidor DNS."

    for prefijo in ("tls://", "https://", "http://", "quic://", "sdns://"):
        if limpio.lower().startswith(prefijo):
            limpio = limpio[len(prefijo):]

    if "/" in limpio:
        limpio = limpio.split("/", 1)[0]
    if ":" in limpio:
        limpio = limpio.split(":", 1)[0]
    limpio = limpio.strip().lower()

    if limpio in MAPA_IP_A_DOT:
        convertido = MAPA_IP_A_DOT[limpio]
        return (
            True,
            convertido,
            f"Se convirtió la IP {limpio} a su servidor DNS privado oficial ({convertido}).",
        )

    if _RE_IPV4.match(limpio):
        return (
            False,
            "",
            "Android DNS Privado requiere un nombre de servidor TLS (por ejemplo "
            "dns.adguard-dns.com u one.one.one.one), no una dirección IP numérica.",
        )

    if not _RE_HOSTNAME.match(limpio):
        return (
            False,
            "",
            f"El servidor '{limpio}' no tiene un formato de dominio válido (ejemplo: dns.adguard-dns.com).",
        )

    return True, limpio, ""


class ADBManager:
    """Gestor de diagnóstico, limpieza de malware/adware y DNS privado por ADB."""

    def __init__(self, base_data_dir: str = "", custom_adb_path: str = ""):
        self.base_data_dir = base_data_dir or os.getcwd()
        self.custom_adb_path = custom_adb_path.strip() if custom_adb_path else ""

    def establecer_ruta_personalizada(self, ruta: str):
        self.custom_adb_path = (ruta or "").strip()

    def resolver_ruta_adb(self) -> tuple[bool, str]:
        """Localiza adb.exe (extrayéndolo a la carpeta portable si viene integrado)."""
        es_win = os.name == "nt"
        ejecutable = "adb.exe" if es_win else "adb"

        if self.custom_adb_path and os.path.isfile(self.custom_adb_path):
            return True, self.custom_adb_path

        carpeta_portable = os.path.join(self.base_data_dir, "platform-tools")
        adb_portable = os.path.join(carpeta_portable, ejecutable)
        if os.path.isfile(adb_portable):
            return True, adb_portable

        # Si el ejecutable empaquetado incluye platform_tools, copiar a data/platform-tools
        # para que el demonio ADB corra desde una carpeta fija y no bloquee _MEIPASS.
        posibles_origenes = []
        meipass = getattr(sys, "_MEIPASS", "")
        if meipass:
            posibles_origenes.append(os.path.join(meipass, "platform_tools"))
        raiz_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        posibles_origenes.append(os.path.join(raiz_proyecto, "platform_tools"))

        for origen in posibles_origenes:
            adb_origen = os.path.join(origen, ejecutable)
            if os.path.isfile(adb_origen):
                try:
                    os.makedirs(carpeta_portable, exist_ok=True)
                    for nombre_arch in (ejecutable, "AdbWinApi.dll", "AdbWinUsbApi.dll"):
                        src = os.path.join(origen, nombre_arch)
                        dst = os.path.join(carpeta_portable, nombre_arch)
                        if os.path.isfile(src) and not os.path.isfile(dst):
                            shutil.copy2(src, dst)
                    if not es_win:
                        os.chmod(adb_portable, 0o755)
                    if os.path.isfile(adb_portable):
                        return True, adb_portable
                except OSError:
                    return True, adb_origen

        # Otras rutas comunes en PC de taller
        candidatos = []
        if getattr(sys, "frozen", False):
            exe_dir = os.path.dirname(os.path.abspath(sys.executable))
            candidatos.append(os.path.join(exe_dir, "platform-tools", ejecutable))
            candidatos.append(os.path.join(exe_dir, ejecutable))

        en_path = shutil.which("adb")
        if en_path:
            candidatos.append(en_path)

        if es_win:
            local_app = os.environ.get("LOCALAPPDATA", "")
            if local_app:
                candidatos.append(
                    os.path.join(local_app, "Android", "Sdk", "platform-tools", "adb.exe")
                )
            candidatos.extend(
                [
                    r"C:\platform-tools\adb.exe",
                    r"C:\adb\adb.exe",
                    r"C:\Android\platform-tools\adb.exe",
                ]
            )

        for ruta in candidatos:
            if ruta and os.path.isfile(ruta):
                return True, ruta

        return False, ""

    def _flags_subproceso(self) -> int:
        if os.name == "nt":
            return int(getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000))
        return 0

    def _ejecutar(
        self, args: list[str], serial: str = "", timeout: int = 12
    ) -> tuple[bool, str, str]:
        ok_adb, ruta_adb = self.resolver_ruta_adb()
        if not ok_adb:
            return (
                False,
                "",
                "No se encontró adb.exe. Usa el botón 'Elegir adb.exe' o descarga la versión compilada con ADB incluido.",
            )

        cmd = [ruta_adb]
        if serial:
            cmd.extend(["-s", serial])
        cmd.extend(args)

        try:
            proc = subprocess.run(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                creationflags=self._flags_subproceso(),
            )
            out = (proc.stdout or b"").decode("utf-8", errors="replace").strip()
            err = (proc.stderr or b"").decode("utf-8", errors="replace").strip()
            return proc.returncode == 0, out, err
        except subprocess.TimeoutExpired:
            return False, "", "Tiempo de espera agotado al comunicarse con el equipo Android."
        except Exception as exc:
            return False, "", f"Error al ejecutar ADB: {exc}"

    def _ejecutar_bytes(
        self, args: list[str], serial: str = "", timeout: int = 15
    ) -> tuple[bool, bytes, str]:
        ok_adb, ruta_adb = self.resolver_ruta_adb()
        if not ok_adb:
            return False, b"", "No se encontró adb.exe."

        cmd = [ruta_adb]
        if serial:
            cmd.extend(["-s", serial])
        cmd.extend(args)

        try:
            proc = subprocess.run(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                creationflags=self._flags_subproceso(),
            )
            err = (proc.stderr or b"").decode("utf-8", errors="replace").strip()
            return proc.returncode == 0, proc.stdout or b"", err
        except subprocess.TimeoutExpired:
            return False, b"", "Tiempo de espera agotado."
        except Exception as exc:
            return False, b"", str(exc)

    def shell(self, comando: str, serial: str = "", timeout: int = 12) -> tuple[bool, str, str]:
        return self._ejecutar(["shell", comando], serial=serial, timeout=timeout)

    # ------------------------------------------
    # CONEXIÓN Y DETECCIÓN DE EQUIPOS
    # ------------------------------------------
    def listar_dispositivos(self) -> dict:
        ok_adb, ruta_adb = self.resolver_ruta_adb()
        if not ok_adb:
            return {
                "adb_ok": False,
                "ruta_adb": "",
                "dispositivos": [],
                "mensaje": "Motor ADB no encontrado. Selecciona adb.exe o usa la compilación oficial.",
            }

        ok, salida, err = self._ejecutar(["devices", "-l"], timeout=10)
        if not ok and not salida:
            return {
                "adb_ok": True,
                "ruta_adb": ruta_adb,
                "dispositivos": [],
                "mensaje": err or "No se pudo consultar la lista de equipos ADB.",
            }

        mapa_estados = {
            "device": "Conectado y listo",
            "unauthorized": "No autorizado (acepta el aviso en la pantalla del celular)",
            "offline": "Sin respuesta (reconecta el cable USB)",
            "recovery": "Modo Recovery",
            "sideload": "Modo Sideload",
            "authorizing": "Autorizando conexión...",
        }

        dispositivos = []
        for linea in salida.splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("List of devices") or linea.startswith("*"):
                continue
            partes = linea.split()
            if len(partes) < 2:
                continue
            serial = partes[0]
            estado = partes[1]
            extras = {}
            for token in partes[2:]:
                if ":" in token:
                    k, v = token.split(":", 1)
                    extras[k] = v

            modelo = extras.get("model", "").replace("_", " ").strip()
            producto = extras.get("product", "").strip()
            dispositivos.append(
                {
                    "serial": serial,
                    "estado": estado,
                    "estado_legible": mapa_estados.get(estado, estado),
                    "modelo": modelo or producto or "Android",
                    "transporte": extras.get("transport_id", ""),
                }
            )

        if not dispositivos:
            msg = (
                "No se detectó ningún equipo Android conectado por USB. "
                "Activa 'Depuración por USB' en el teléfono y verifica el cable."
            )
        else:
            listos = sum(1 for d in dispositivos if d["estado"] == "device")
            no_aut = sum(1 for d in dispositivos if d["estado"] == "unauthorized")
            if listos > 0:
                msg = f"{listos} equipo(s) conectado(s) y listo(s) para trabajar."
            elif no_aut > 0:
                msg = (
                    "Equipo detectado pero NO AUTORIZADO. Desbloquea el celular, "
                    "marca 'Permitir siempre' y toca Permitir."
                )
            else:
                msg = f"Se detectaron {len(dispositivos)} equipo(s) en estado especial."

        return {
            "adb_ok": True,
            "ruta_adb": ruta_adb,
            "dispositivos": dispositivos,
            "mensaje": msg,
        }

    def reiniciar_servidor(self) -> tuple[bool, str]:
        ok_adb, _ = self.resolver_ruta_adb()
        if not ok_adb:
            return False, "No se encontró adb.exe."
        self._ejecutar(["kill-server"], timeout=8)
        ok, out, err = self._ejecutar(["start-server"], timeout=12)
        if ok:
            return True, "Servidor ADB reiniciado correctamente."
        return False, err or out or "No se pudo reiniciar el servidor ADB."

    # ------------------------------------------
    # 1. DIAGNÓSTICO COMPLETO POR ADB
    # ------------------------------------------
    @staticmethod
    def _parsear_getprop(texto: str) -> dict[str, str]:
        props: dict[str, str] = {}
        patron = re.compile(r"^\[([^\]]+)\]:\s*\[(.*)\]$")
        for linea in texto.splitlines():
            m = patron.match(linea.strip())
            if m:
                props[m.group(1)] = m.group(2).strip()
        return props

    @staticmethod
    def _parsear_bateria(texto: str) -> dict:
        datos: dict[str, str] = {}
        for linea in texto.splitlines():
            if ":" in linea:
                k, v = linea.split(":", 1)
                datos[k.strip().lower()] = v.strip()

        def _leer_int(clave: str, defecto: int = 0) -> int:
            val = datos.get(clave, "")
            return int(val) if val.lstrip("-").isdigit() else defecto

        nivel = _leer_int("level", -1)
        temp_raw = _leer_int("temperature", 0)
        temp_c = round(temp_raw / 10.0, 1) if temp_raw > 0 else 0.0
        volt_mv = _leer_int("voltage", 0)

        mapa_status = {
            "2": "Cargando",
            "3": "Descargando",
            "4": "Sin cargar",
            "5": "Carga completa",
        }
        mapa_health = {
            "2": "Buena",
            "3": "Sobrecalentamiento",
            "4": "Dañada / Muerta",
            "5": "Sobrevoltaje",
            "6": "Fallo general",
            "7": "Temperatura baja",
        }

        fuentes = []
        if datos.get("ac powered", "").lower() == "true":
            fuentes.append("Cargador CA")
        if datos.get("usb powered", "").lower() == "true":
            fuentes.append("Puerto USB")
        if datos.get("wireless powered", "").lower() == "true":
            fuentes.append("Inalámbrica")

        contador_uah = _leer_int("charge counter", 0)
        capacidad_mah = round(contador_uah / 1000) if contador_uah > 1000 else 0

        alerta_temp = temp_c >= 42.0
        salud_txt = mapa_health.get(datos.get("health", ""), "Desconocida")
        if alerta_temp and salud_txt == "Buena":
            salud_txt = "Buena (Temperatura elevada)"

        return {
            "nivel": nivel,
            "estado": mapa_status.get(datos.get("status", ""), "Desconocido"),
            "salud": salud_txt,
            "temperatura_c": temp_c,
            "alerta_temperatura": alerta_temp,
            "voltaje_mv": volt_mv,
            "fuente": ", ".join(fuentes) if fuentes else "Batería",
            "tecnologia": datos.get("technology", "Li-ion") or "Li-ion",
            "contador_mah": capacidad_mah,
        }

    @staticmethod
    def _parsear_almacenamiento(texto_df: str) -> dict:
        lineas = [l.strip() for l in texto_df.splitlines() if l.strip()]
        if len(lineas) < 2:
            return {"resumen": "No disponible", "total_gb": 0.0, "libre_gb": 0.0, "porcentaje": 0}

        # Toma los tokens enteros separados por espacio después del nombre del dispositivo
        unido = " ".join(lineas[1:])
        nums = [int(tok) for tok in unido.split()[1:] if tok.isdigit()]
        if len(nums) >= 3:
            total_kb = nums[0]
            usado_kb = nums[1]
            disp_kb = nums[2]
            if total_kb > 0:
                total_gb = total_kb / (1024 * 1024)
                usado_gb = usado_kb / (1024 * 1024)
                libre_gb = disp_kb / (1024 * 1024)
                pct = min(100, round((usado_kb / total_kb) * 100))
                return {
                    "total_gb": round(total_gb, 1),
                    "usado_gb": round(usado_gb, 1),
                    "libre_gb": round(libre_gb, 1),
                    "porcentaje": pct,
                    "resumen": f"{usado_gb:.1f} GB usados de {total_gb:.1f} GB ({pct}%) · {libre_gb:.1f} GB libres",
                }
        return {"resumen": "No disponible", "total_gb": 0.0, "libre_gb": 0.0, "porcentaje": 0}

    @staticmethod
    def _parsear_ram(texto_mem: str) -> dict:
        valores: dict[str, int] = {}
        for linea in texto_mem.splitlines():
            m = re.match(r"^([A-Za-z_()]+):\s*(\d+)", linea.strip())
            if m:
                valores[m.group(1)] = int(m.group(2))

        total_kb = valores.get("MemTotal", 0)
        disp_kb = valores.get("MemAvailable", 0)
        if disp_kb <= 0:
            disp_kb = (
                valores.get("MemFree", 0)
                + valores.get("Buffers", 0)
                + valores.get("Cached", 0)
            )
        if total_kb <= 0:
            return {"resumen": "No disponible", "total_gb": 0.0, "disponible_gb": 0.0}

        total_gb = total_kb / (1024 * 1024)
        disp_gb = disp_kb / (1024 * 1024)
        usado_gb = max(0.0, total_gb - disp_gb)
        pct = min(100, round((usado_gb / total_gb) * 100))
        return {
            "total_gb": round(total_gb, 1),
            "disponible_gb": round(disp_gb, 1),
            "porcentaje": pct,
            "resumen": f"{disp_gb:.1f} GB libres de {total_gb:.1f} GB ({pct}% en uso)",
        }

    @staticmethod
    def _extraer_imei_parcel(salida: str) -> str:
        if not salida or "Parcel" not in salida:
            return ""
        fragmentos = re.findall(r"'([0-9. ]+)'", salida)
        digitos = "".join(ch for frag in fragmentos for ch in frag if ch.isdigit())
        if 14 <= len(digitos) <= 17:
            return digitos
        return ""

    @staticmethod
    def _formatear_uptime(texto_uptime: str) -> str:
        if not texto_uptime:
            return "No disponible"
        partes = texto_uptime.strip().split()
        try:
            segundos = int(float(partes[0]))
            dias, resto = divmod(segundos, 86400)
            horas, resto = divmod(resto, 3600)
            minutos, _ = divmod(resto, 60)
            if dias > 0:
                return f"{dias}d {horas}h {minutos}m"
            return f"{horas}h {minutos}m"
        except Exception:
            return "No disponible"

    def diagnosticar_equipo(self, serial: str) -> dict:
        if not serial:
            return {"ok": False, "error": "Selecciona un equipo conectado."}

        ok_p, txt_props, err_p = self.shell("getprop", serial=serial, timeout=12)
        if not ok_p or not txt_props:
            return {
                "ok": False,
                "error": err_p or "No se pudo leer la información del equipo. Verifica que esté autorizado.",
            }

        props = self._parsear_getprop(txt_props)
        _, txt_bat, _ = self.shell("dumpsys battery", serial=serial, timeout=10)
        _, txt_df, _ = self.shell("df -k /data", serial=serial, timeout=8)
        _, txt_mem, _ = self.shell("cat /proc/meminfo", serial=serial, timeout=8)
        _, txt_size, _ = self.shell("wm size", serial=serial, timeout=6)
        _, txt_dens, _ = self.shell("wm density", serial=serial, timeout=6)
        _, txt_up, _ = self.shell("cat /proc/uptime", serial=serial, timeout=6)
        _, txt_imei, _ = self.shell(
            "service call iphonesubinfo 1 s16 com.android.shell", serial=serial, timeout=6
        )
        dns_info = self.obtener_estado_dns(serial)

        marca = (
            props.get("ro.product.brand")
            or props.get("ro.product.manufacturer")
            or "Android"
        ).strip()
        if marca:
            marca = marca[0].upper() + marca[1:]
        fabricante = (props.get("ro.product.manufacturer") or marca).strip()
        modelo = (props.get("ro.product.model") or props.get("ro.product.name") or "Desconocido").strip()
        nombre_cod = (props.get("ro.product.device") or props.get("ro.build.product") or "").strip()
        android_ver = props.get("ro.build.version.release", "?")
        sdk_ver = props.get("ro.build.version.sdk", "?")
        parche_seg = props.get("ro.build.version.security_patch", "No disponible")
        compilacion = props.get("ro.build.display.id", "")
        procesador = (
            props.get("ro.soc.model")
            or props.get("ro.hardware.chipname")
            or props.get("ro.board.platform")
            or props.get("ro.hardware")
            or "No especificado"
        )
        abi = props.get("ro.product.cpu.abi", "")
        serie_real = (
            props.get("ro.serialno")
            or props.get("ro.boot.serialno")
            or serial
        )
        operador = (
            props.get("gsm.sim.operator.alpha")
            or props.get("gsm.operator.alpha")
            or "Sin SIM / No detectado"
        ).strip(", ")
        bootloader_lock = props.get("ro.boot.flash.locked", "")
        estado_boot = (
            "Bloqueado (Original)"
            if bootloader_lock == "1"
            else ("Desbloqueado" if bootloader_lock == "0" else props.get("ro.boot.verifiedbootstate", "Estándar"))
        )

        imei = self._extraer_imei_parcel(txt_imei) or "Protegido por Android (*#06#)"
        bateria = self._parsear_bateria(txt_bat)
        almacenamiento = self._parsear_almacenamiento(txt_df)
        ram = self._parsear_ram(txt_mem)
        uptime_txt = self._formatear_uptime(txt_up)

        res_pantalla = " / ".join(
            l.replace("Physical size:", "Física:").replace("Override size:", "Modificada:").strip()
            for l in txt_size.splitlines()
            if l.strip()
        ) or "No disponible"
        dens_pantalla = " / ".join(
            l.replace("Physical density:", "Física:").replace("Override density:", "Modificada:").strip()
            for l in txt_dens.splitlines()
            if l.strip()
        ) or "No disponible"

        nivel_txt = f"{bateria['nivel']}%" if bateria["nivel"] >= 0 else "N/D"
        volt_txt = f"{bateria['voltaje_mv']} mV" if bateria["voltaje_mv"] > 0 else "N/D"
        temp_txt = f"{bateria['temperatura_c']} °C" if bateria["temperatura_c"] > 0 else "N/D"

        lineas_reporte = [
            f"=== DIAGNÓSTICO TÉCNICO ADB ({datetime.now().strftime('%d/%m/%Y %H:%M')}) ===",
            "",
            "[IDENTIFICACIÓN DEL EQUIPO]",
            f"  Marca / Fabricante : {marca} ({fabricante})",
            f"  Modelo             : {modelo}" + (f" ({nombre_cod})" if nombre_cod else ""),
            f"  Número de serie    : {serie_real}",
            f"  IMEI               : {imei}",
            f"  Operador / SIM     : {operador or 'No detectado'}",
            "",
            "[SISTEMA Y HARDWARE]",
            f"  Versión Android    : Android {android_ver} (API {sdk_ver})",
            f"  Parche seguridad   : {parche_seg}",
            f"  Compilación        : {compilacion}",
            f"  Procesador / SoC   : {procesador}" + (f" ({abi})" if abi else ""),
            f"  Bootloader         : {estado_boot}",
            f"  Tiempo encendido   : {uptime_txt}",
            "",
            "[BATERÍA Y CARGA]",
            f"  Nivel actual       : {nivel_txt} ({bateria['estado']})",
            f"  Salud reportada    : {bateria['salud']}",
            f"  Temperatura        : {temp_txt}" + ("  [¡ALERTA: TEMPERATURA ALTA!]" if bateria["alerta_temperatura"] else ""),
            f"  Voltaje / Fuente   : {volt_txt} · {bateria['fuente']} ({bateria['tecnologia']})",
            "",
            "[MEMORIA Y PANTALLA]",
            f"  Almacenamiento     : {almacenamiento['resumen']}",
            f"  Memoria RAM        : {ram['resumen']}",
            f"  Resolución         : {res_pantalla}",
            f"  Densidad (DPI)     : {dens_pantalla}",
            "",
            "[RED Y DNS PRIVADO]",
            f"  Estado DNS         : {dns_info.get('descripcion_corta', 'No disponible')}",
        ]

        return {
            "ok": True,
            "serial": serial,
            "serie_real": serie_real,
            "marca": marca,
            "fabricante": fabricante,
            "modelo": modelo,
            "nombre_codigo": nombre_cod,
            "imei": imei,
            "android_version": android_ver,
            "sdk_int": sdk_ver,
            "parche_seguridad": parche_seg,
            "procesador": procesador,
            "bateria": bateria,
            "almacenamiento": almacenamiento,
            "ram": ram,
            "pantalla": res_pantalla,
            "dns": dns_info,
            "texto_reporte": "\n".join(lineas_reporte),
        }

    def capturar_pantalla(self, serial: str, ruta_destino: str) -> tuple[bool, str]:
        if not serial:
            return False, "Selecciona un equipo conectado."
        ok, datos_png, err = self._ejecutar_bytes(
            ["exec-out", "screencap", "-p"], serial=serial, timeout=15
        )
        # Firma estándar PNG: 89 50 4E 47
        if not ok or not datos_png or not datos_png.startswith(b"\x89PNG"):
            return (
                False,
                err or "No se pudo capturar la pantalla (puede estar bloqueada por seguridad o apagada).",
            )
        os.makedirs(os.path.dirname(os.path.abspath(ruta_destino)), exist_ok=True)
        with open(ruta_destino, "wb") as f:
            f.write(datos_png)
        return True, ruta_destino

    def reiniciar_equipo(self, serial: str, modo: str = "") -> tuple[bool, str]:
        if not serial:
            return False, "Selecciona un equipo conectado."
        args = ["reboot"]
        if modo in ("recovery", "bootloader"):
            args.append(modo)
        ok, out, err = self._ejecutar(args, serial=serial, timeout=10)
        if ok:
            etiqueta = modo.capitalize() if modo else "Normal"
            return True, f"Se envió la orden de reinicio ({etiqueta}) al equipo."
        return False, err or out or "No se pudo reiniciar el equipo."

    # ------------------------------------------
    # 2. ESCANEO Y REMOCIÓN DE MALWARE / ADWARE
    # ------------------------------------------
    @staticmethod
    def _extraer_paquetes_appops(texto: str) -> set[str]:
        encontrados: set[str] = set()
        for linea in texto.splitlines():
            limpia = linea.strip()
            if not limpia or limpia.startswith("Error") or limpia.startswith("No operations"):
                continue
            # appops query-op devuelve un paquete por línea
            token = limpia.split()[0].strip()
            if "." in token and _RE_PAQUETE.match(token):
                encontrados.add(token)
        return encontrados

    @classmethod
    def _es_app_confiable(cls, pkg: str) -> bool:
        if pkg in PAQUETES_SISTEMA_BLOQUEADOS:
            return True
        return any(pkg.startswith(pref) for pref in PREFIJOS_APPS_CONFIABLES)

    @classmethod
    def _evaluar_riesgo_paquete(
        cls,
        pkg: str,
        ruta_apk: str,
        tiene_overlay: bool,
        instala_apks: bool,
    ) -> tuple[int, str, list[str]]:
        """Clasifica el nivel de riesgo de una app instalada por el usuario.

        Devuelve (prioridad: 2=Alto, 1=Medio, 0=Normal, etiqueta_riesgo, motivos).
        """
        if cls._es_app_confiable(pkg):
            motivos_ok = []
            if tiene_overlay:
                motivos_ok.append("App conocida (permiso superposición)")
            return 0, "Normal (Conocida)", motivos_ok or ["Aplicación común reconocida"]

        pkg_low = pkg.lower()
        motivos: list[str] = []
        puntaje = 0

        # 1. Camuflaje haciéndose pasar por paquete interno de Android en partición de usuario
        if pkg_low.startswith(("com.android.", "com.google.system", "android.system")):
            puntaje += 3
            motivos.append("Se camufla como paquete de sistema en espacio de usuario")

        # 2. Nombre de paquete anómalo (segmentos de 1 letra o generados al azar)
        segmentos = pkg_low.split(".")
        if len(segmentos) >= 2 and all(len(s) <= 2 for s in segmentos[1:]):
            puntaje += 3
            motivos.append("Identificador corto/oculto típico de adware invisible")

        # 3. Patrones de falsos limpiadores / boosters / adware conocido
        for patron_re, desc in PATRONES_ALTO_RIESGO:
            if re.search(patron_re, pkg_low):
                puntaje += 3
                motivos.append(desc)
                break
        else:
            for patron_re, desc in PATRONES_RIESGO_MEDIO:
                if re.search(patron_re, pkg_low):
                    puntaje += 1
                    motivos.append(desc)
                    break

        # 4. Permisos críticos usados por adware de pantalla completa
        if tiene_overlay:
            puntaje += 2
            motivos.append("Permiso activo: Mostrar anuncios sobre otras apps")

        if instala_apks:
            puntaje += 2
            motivos.append("Permiso activo: Instalar APKs externos")

        if ruta_apk and "/mnt/expand/" in ruta_apk:
            motivos.append("Instalada en memoria externa")

        if puntaje >= 3:
            return 2, "ALTO (Sospechosa)", motivos
        if puntaje >= 1:
            return 1, "REVISAR", motivos
        return 0, "Normal (Usuario)", motivos or ["Instalada por el usuario"]

    def escanear_malware(self, serial: str) -> dict:
        if not serial:
            return {"ok": False, "error": "Selecciona un equipo conectado.", "apps": []}

        ok_l, txt_pkgs, err_l = self.shell("pm list packages -3 -f", serial=serial, timeout=15)
        if not ok_l and not txt_pkgs:
            # Respaldo sin -f para equipos con implementación recortada
            ok_l, txt_pkgs, err_l = self.shell("pm list packages -3", serial=serial, timeout=15)
            if not ok_l and not txt_pkgs:
                return {
                    "ok": False,
                    "error": err_l or "No se pudo listar las aplicaciones del equipo.",
                    "apps": [],
                }

        _, txt_deshab, _ = self.shell("pm list packages -d -3", serial=serial, timeout=10)
        _, txt_overlay, _ = self.shell(
            "appops query-op SYSTEM_ALERT_WINDOW allow", serial=serial, timeout=10
        )
        _, txt_install, _ = self.shell(
            "appops query-op REQUEST_INSTALL_PACKAGES allow", serial=serial, timeout=10
        )

        deshabilitadas = {
            l.replace("package:", "").strip()
            for l in txt_deshab.splitlines()
            if l.strip().startswith("package:")
        }
        con_overlay = self._extraer_paquetes_appops(txt_overlay)
        con_install = self._extraer_paquetes_appops(txt_install)

        apps = []
        vistos: set[str] = set()
        for linea in txt_pkgs.splitlines():
            linea = linea.strip()
            if not linea.startswith("package:"):
                continue
            contenido = linea[len("package:"):]
            # En Android 11+ la ruta contiene '==' en carpetas cifradas: usar rsplit("=", 1)
            if ".apk=" in contenido or "=" in contenido:
                ruta_apk, pkg = contenido.rsplit("=", 1)
            else:
                ruta_apk, pkg = "", contenido

            pkg = pkg.strip()
            if not pkg or pkg in vistos or not _RE_PAQUETE.match(pkg):
                continue
            vistos.add(pkg)

            ov = pkg in con_overlay
            inst = pkg in con_install
            prioridad, etiqueta_riesgo, motivos = self._evaluar_riesgo_paquete(
                pkg, ruta_apk, ov, inst
            )
            apps.append(
                {
                    "package": pkg,
                    "ruta_apk": ruta_apk,
                    "prioridad": prioridad,
                    "riesgo": etiqueta_riesgo,
                    "estado": "Desactivada" if pkg in deshabilitadas else "Activa",
                    "tiene_overlay": ov,
                    "instala_apks": inst,
                    "motivos": " · ".join(motivos),
                }
            )

        apps.sort(key=lambda x: (-x["prioridad"], x["package"].lower()))
        sospechosas = sum(1 for a in apps if a["prioridad"] >= 1)
        alto_riesgo = sum(1 for a in apps if a["prioridad"] >= 2)

        return {
            "ok": True,
            "apps": apps,
            "total": len(apps),
            "sospechosas": sospechosas,
            "alto_riesgo": alto_riesgo,
        }

    def detectar_app_en_pantalla(self, serial: str) -> dict:
        """Detecta qué paquete está mostrando una ventana o anuncio en primer plano."""
        if not serial:
            return {"ok": False, "error": "Selecciona un equipo conectado."}

        _, txt_win, _ = self.shell(
            "dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'", serial=serial, timeout=8
        )
        _, txt_act, _ = self.shell(
            "dumpsys activity activities | grep -E 'topResumedActivity|mResumedActivity'",
            serial=serial,
            timeout=8,
        )
        combinado = f"{txt_act}\n{txt_win}"
        # Busca patrones tipo com.paquete.app/com.paquete.Actividad
        coincidencias = re.findall(r"([A-Za-z0-9_]+(?:\.[A-Za-z0-9_]+)+)/[A-Za-z0-9_.$]+", combinado)
        ignorar = {"com.android.systemui"}
        paquete_detectado = ""
        for cand in coincidencias:
            if cand not in ignorar:
                paquete_detectado = cand
                break
        if not paquete_detectado and coincidencias:
            paquete_detectado = coincidencias[0]

        if not paquete_detectado:
            return {
                "ok": False,
                "error": "No se pudo identificar la ventana activa (verifica que la pantalla esté encendida y desbloqueada).",
            }

        _, txt_u, _ = self.shell("pm list packages -3", serial=serial, timeout=8)
        apps_usuario = {
            l.replace("package:", "").strip()
            for l in txt_u.splitlines()
            if l.strip().startswith("package:")
        }
        es_usuario = paquete_detectado in apps_usuario
        es_protegido = paquete_detectado in PAQUETES_SISTEMA_BLOQUEADOS

        return {
            "ok": True,
            "package": paquete_detectado,
            "es_usuario": es_usuario,
            "es_protegido": es_protegido,
        }

    def desinstalar_paquete(self, serial: str, package: str) -> tuple[bool, str]:
        pkg = (package or "").strip()
        if not pkg or not _RE_PAQUETE.match(pkg):
            return False, f"Nombre de paquete inválido: {pkg}"
        if pkg in PAQUETES_SISTEMA_BLOQUEADOS:
            return False, f"Protección activa: '{pkg}' es un componente crítico de Android y no debe borrarse."

        # Cerrar procesos primero
        self.shell(f"am force-stop {pkg}", serial=serial, timeout=6)

        ok, out, err = self.shell(f"pm uninstall {pkg}", serial=serial, timeout=15)
        if ok and "Success" in out:
            return True, f"Desinstalada completamente: {pkg}"

        # Respaldo para apps preinstaladas en el perfil del usuario 0
        ok2, out2, err2 = self.shell(f"pm uninstall --user 0 {pkg}", serial=serial, timeout=15)
        if ok2 and "Success" in out2:
            return True, f"Eliminada para el usuario actual: {pkg}"

        detalle = out2 or err2 or out or err or "Error desconocido"
        return False, f"No se pudo desinstalar {pkg}: {detalle}"

    def desactivar_paquete(self, serial: str, package: str) -> tuple[bool, str]:
        pkg = (package or "").strip()
        if not pkg or not _RE_PAQUETE.match(pkg):
            return False, f"Nombre de paquete inválido: {pkg}"
        if pkg in PAQUETES_SISTEMA_BLOQUEADOS:
            return False, f"Protección activa: '{pkg}' es esencial para Android."

        self.shell(f"am force-stop {pkg}", serial=serial, timeout=6)
        ok, out, err = self.shell(f"pm disable-user --user 0 {pkg}", serial=serial, timeout=10)
        if ok and ("disabled" in out.lower() or "new state" in out.lower()):
            return True, f"Aplicación congelada/desactivada: {pkg}"
        return False, f"No se pudo desactivar {pkg}: {out or err}"

    def revocar_superposicion(self, serial: str, package: str) -> tuple[bool, str]:
        pkg = (package or "").strip()
        if not pkg or not _RE_PAQUETE.match(pkg):
            return False, f"Nombre de paquete inválido: {pkg}"
        self.shell(f"am force-stop {pkg}", serial=serial, timeout=6)
        ok, out, err = self.shell(
            f"appops set {pkg} SYSTEM_ALERT_WINDOW ignore", serial=serial, timeout=8
        )
        self.shell(
            f"appops set {pkg} REQUEST_INSTALL_PACKAGES ignore", serial=serial, timeout=8
        )
        if ok:
            return True, f"Permisos de anuncios flotantes e instalación bloqueados en: {pkg}"
        return False, err or out or f"No se pudo cambiar permisos de {pkg}"

    def limpiar_spam_navegador(
        self, serial: str, package: str = "com.android.chrome"
    ) -> tuple[bool, str]:
        pkg = (package or "").strip()
        if not pkg or not _RE_PAQUETE.match(pkg):
            return False, "Paquete de navegador inválido."
        ok, out, err = self.shell(f"pm clear {pkg}", serial=serial, timeout=12)
        if ok and "Success" in out:
            return (
                True,
                f"Se limpiaron notificaciones basura, caché y sitios maliciosos de {pkg}.",
            )
        return False, f"No se pudo limpiar {pkg} (verifica si está instalado): {out or err}"

    # ------------------------------------------
    # 3. ANCLAR DNS PRIVADO POR ADB
    # ------------------------------------------
    def obtener_estado_dns(self, serial: str) -> dict:
        if not serial:
            return {
                "ok": False,
                "modo": "",
                "servidor": "",
                "descripcion_corta": "Sin equipo seleccionado",
            }

        ok_m, modo_raw, err_m = self.shell(
            "settings get global private_dns_mode", serial=serial, timeout=8
        )
        _, spec_raw, _ = self.shell(
            "settings get global private_dns_specifier", serial=serial, timeout=8
        )
        if not ok_m and err_m:
            return {
                "ok": False,
                "modo": "",
                "servidor": "",
                "descripcion_corta": err_m,
            }

        modo = (modo_raw or "").strip().lower()
        if modo in ("null", ""):
            modo = "opportunistic"
        servidor = (spec_raw or "").strip()
        if servidor.lower() == "null":
            servidor = ""

        if modo == "hostname":
            desc = f"Anclado fijo → {servidor or '(sin servidor)'}"
        elif modo == "off":
            desc = "Desactivado (usa DNS de red normal)"
        else:
            desc = "Automático de fábrica (opportunistic)"

        return {
            "ok": True,
            "modo": modo,
            "servidor": servidor,
            "descripcion_corta": desc,
        }

    def anclar_dns(self, serial: str, servidor_dns: str) -> tuple[bool, str]:
        if not serial:
            return False, "Selecciona un equipo conectado."

        valido, hostname, aviso = normalizar_hostname_dns(servidor_dns)
        if not valido:
            return False, aviso

        _, sdk_txt, _ = self.shell("getprop ro.build.version.sdk", serial=serial, timeout=6)
        if sdk_txt.strip().isdigit() and int(sdk_txt.strip()) < 28:
            return (
                False,
                f"Este equipo tiene Android antiguo (SDK {sdk_txt.strip()}). "
                "La función nativa de DNS Privado global requiere Android 9.0 o superior.",
            )

        ok1, _, err1 = self.shell(
            f"settings put global private_dns_specifier {hostname}",
            serial=serial,
            timeout=8,
        )
        ok2, _, err2 = self.shell(
            "settings put global private_dns_mode hostname",
            serial=serial,
            timeout=8,
        )
        if not (ok1 and ok2):
            return False, err1 or err2 or "Android rechazó el cambio de configuración DNS."

        verif = self.obtener_estado_dns(serial)
        if verif.get("modo") == "hostname" and verif.get("servidor") == hostname:
            extra = f"\nNota: {aviso}" if aviso else ""
            return (
                True,
                f"DNS anclado correctamente en el equipo:\n• Servidor: {hostname}\n"
                f"• Aplica en Wi-Fi y Datos móviles (se mantiene aunque reinicies el celular).{extra}",
            )
        return (
            False,
            "Se envió el comando, pero el equipo no confirmó el cambio (algunas capas empresariales lo restringen).",
        )

    def restaurar_dns_automatico(self, serial: str) -> tuple[bool, str]:
        if not serial:
            return False, "Selecciona un equipo conectado."
        ok, _, err = self.shell(
            "settings put global private_dns_mode opportunistic",
            serial=serial,
            timeout=8,
        )
        self.shell("settings delete global private_dns_specifier", serial=serial, timeout=6)
        if ok:
            return True, "DNS restaurado al modo Automático original de Android."
        return False, err or "No se pudo restaurar el modo automático."

    def desactivar_dns_privado(self, serial: str) -> tuple[bool, str]:
        if not serial:
            return False, "Selecciona un equipo conectado."
        ok, _, err = self.shell(
            "settings put global private_dns_mode off",
            serial=serial,
            timeout=8,
        )
        if ok:
            return True, "DNS Privado desactivado (off)."
        return False, err or "No se pudo desactivar el DNS Privado."

    def probar_conectividad_dns(self, serial: str) -> tuple[bool, str]:
        if not serial:
            return False, "Selecciona un equipo conectado."
        estado = self.obtener_estado_dns(serial)
        ok, out, err = self.shell("ping -c 2 -W 3 google.com", serial=serial, timeout=10)
        if ok and ("bytes from" in out or "0% packet loss" in out):
            return (
                True,
                f"Conexión y resolución DNS exitosas desde el celular.\n"
                f"DNS actual: {estado.get('descripcion_corta', '')}",
            )
        return (
            False,
            "El teléfono no pudo resolver/conectar a internet en la prueba.\n"
            "Verifica que el celular tenga Wi-Fi o datos encendidos y que el servidor DNS escrito sea correcto.\n"
            f"Detalle: {out or err or 'Sin respuesta de red'}",
        )
