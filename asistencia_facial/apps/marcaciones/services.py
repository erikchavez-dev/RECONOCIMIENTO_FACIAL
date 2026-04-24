"""
apps/marcaciones/services.py

Lógica de marcación según el diagrama definitivo:
- NUNCA bloquea: toda marcación se guarda en historial.
- va_a_asistencia=True solo cuando la marcación cuenta para asistencia.
- Días no laborables (sáb/dom) → SOLO_VERIFICACION, no afecta asistencia.
- Tolerancia configurable: hora_fin_entrada + tolerancia_minutos → TARDANZA.
- Cierre de día: después de hora_fin_salida no se altera la asistencia.
"""

import datetime
from django.utils import timezone
from zoneinfo import ZoneInfo
from .models import Marcacion
from apps.configuracion.models import ConfiguracionSistema


def _es_dia_laborable(fecha_date):
    """Lunes=0 … Viernes=4 son laborables. Sáb=5, Dom=6 no."""
    return fecha_date.weekday() < 5


def _tiempo_como_datetime(t, fecha_date, tz):
    """Convierte un time + date en un datetime con timezone."""
    return datetime.datetime(
        fecha_date.year, fecha_date.month, fecha_date.day,
        t.hour, t.minute, t.second,
        tzinfo=tz
    )


def _sumar_minutos(t, minutos):
    """Suma minutos a un time. Retorna time."""
    dt = datetime.datetime(2000, 1, 1, t.hour, t.minute, t.second)
    dt += datetime.timedelta(minutes=minutos)
    return dt.time()


def registrar_marcacion(
    trabajador,
    ip,
    dispositivo,
    latitud=None,
    longitud=None,
    ciudad=None,
    pais=None,
    ip_info=None,
):
    """
    Registra SIEMPRE una marcación en el historial.
    Retorna (marcacion, mensaje_informativo).
    NUNCA retorna (None, error) salvo falta de configuración.
    """
    config = ConfiguracionSistema.objects.first()
    if not config:
        return None, 'No hay configuración del sistema'

    lima_tz   = ZoneInfo('America/Lima')
    ahora_lim = timezone.localtime(timezone.now(), lima_tz)
    hora_act  = ahora_lim.time()
    hoy       = ahora_lim.date()

    inicio_dia = ahora_lim.replace(hour=0,  minute=0,  second=0,  microsecond=0)
    fin_dia    = ahora_lim.replace(hour=23, minute=59, second=59, microsecond=999999)

    # ── Tolerancia: límite hasta el cual aún se acepta como TARDANZA ─────
    tolerancia = getattr(config, 'tolerancia_minutos', 30)
    hora_limite_tardanza = _sumar_minutos(config.hora_fin_entrada, tolerancia)

    # ══════════════════════════════════════════════════════════════════════
    # PASO 1 — ¿Es día laborable?
    # ══════════════════════════════════════════════════════════════════════
    if not _es_dia_laborable(hoy):
        marcacion = Marcacion.objects.create(
            trabajador      = trabajador,
            fecha           = ahora_lim,
            tipo            = 'SOLO_VERIFICACION',
            estado          = None,
            ip              = ip,
            dispositivo     = dispositivo,
            exitoso         = True,
            va_a_asistencia = False,
            latitud         = latitud or None,
            longitud        = longitud or None,
            ciudad          = ciudad   or None,
            pais            = pais     or None,
            ip_info         = ip_info  or None,
        )
        return marcacion, 'No es día laborable. Se registró la visita en historial.'

    # ══════════════════════════════════════════════════════════════════════
    # PASO 2 — Obtener marcaciones del día (solo las que afectan asistencia)
    # ══════════════════════════════════════════════════════════════════════
    marcaciones_hoy = Marcacion.objects.filter(
        trabajador      = trabajador,
        fecha__gte      = inicio_dia,
        fecha__lte      = fin_dia,
        exitoso         = True,
        va_a_asistencia = True,
    )
    entrada_hoy = marcaciones_hoy.filter(
        tipo__in=['ENTRADA_VALIDA', 'ENTRADA']
    ).order_by('fecha').first()
    salida_hoy  = marcaciones_hoy.filter(
        tipo__in=['SALIDA_VALIDA', 'SALIDA']
    ).order_by('fecha').first()

    # ── Rangos horarios ───────────────────────────────────────────────────
    en_rango_entrada_puntual = (
        config.hora_inicio_entrada <= hora_act <= config.hora_fin_entrada
    )
    en_rango_tardanza = (
        config.hora_fin_entrada < hora_act <= hora_limite_tardanza
    )
    en_rango_salida = (
        config.hora_inicio_salida <= hora_act <= config.hora_fin_salida
    )
    # Después de todo horario de salida → día cerrado
    dia_cerrado = hora_act > config.hora_fin_salida

    # ══════════════════════════════════════════════════════════════════════
    # PASO 3 — Evaluar según si tiene entrada o no
    # ══════════════════════════════════════════════════════════════════════

    if not entrada_hoy:
        # ── Sin entrada: evaluar franja ───────────────────────────────────

        if hora_act < config.hora_inicio_entrada:
            # Antes del horario de entrada → FUERA_HORARIO
            marcacion = _crear_marcacion(
                trabajador, ahora_lim, 'FUERA_HORARIO', None,
                ip, dispositivo, False,
                latitud, longitud, ciudad, pais, ip_info
            )
            return marcacion, 'Aún no es hora de entrada. Marcación registrada en historial.'

        elif en_rango_entrada_puntual:
            # ENTRADA PUNTUAL
            marcacion = _crear_marcacion(
                trabajador, ahora_lim, 'ENTRADA_VALIDA', 'PUNTUAL',
                ip, dispositivo, True,
                latitud, longitud, ciudad, pais, ip_info
            )
            return marcacion, 'Entrada puntual registrada correctamente.'

        elif en_rango_tardanza:
            # ENTRADA TARDANZA (dentro del margen de tolerancia)
            marcacion = _crear_marcacion(
                trabajador, ahora_lim, 'ENTRADA_VALIDA', 'TARDANZA',
                ip, dispositivo, True,
                latitud, longitud, ciudad, pais, ip_info
            )
            return marcacion, 'Entrada con tardanza registrada.'

        elif en_rango_salida:
            # En horario de salida sin entrada → intento inválido
            marcacion = _crear_marcacion(
                trabajador, ahora_lim, 'FUERA_HORARIO', None,
                ip, dispositivo, False,
                latitud, longitud, ciudad, pais, ip_info
            )
            return marcacion, 'No tiene entrada registrada. No se puede marcar salida.'

        else:
            # Entre fin de tardanza e inicio de salida → FUERA_HORARIO
            marcacion = _crear_marcacion(
                trabajador, ahora_lim, 'FUERA_HORARIO', None,
                ip, dispositivo, False,
                latitud, longitud, ciudad, pais, ip_info
            )
            return marcacion, 'Fuera del horario de marcación.'

    else:
        # ── Con entrada, sin salida ───────────────────────────────────────

        if salida_hoy:
            # Ya marcó entrada y salida
            marcacion = _crear_marcacion(
                trabajador, ahora_lim, 'FUERA_HORARIO', None,
                ip, dispositivo, False,
                latitud, longitud, ciudad, pais, ip_info
            )
            return marcacion, 'Ya registró su entrada y salida de hoy.'

        if dia_cerrado:
            # Día ya cerrado → no afecta asistencia
            marcacion = _crear_marcacion(
                trabajador, ahora_lim, 'FUERA_HORARIO', None,
                ip, dispositivo, False,
                latitud, longitud, ciudad, pais, ip_info
            )
            return marcacion, 'El horario de salida ya cerró. Marcación registrada en historial.'

        if hora_act < config.hora_inicio_salida:
            # Aún no es hora de salida
            marcacion = _crear_marcacion(
                trabajador, ahora_lim, 'FUERA_HORARIO', None,
                ip, dispositivo, False,
                latitud, longitud, ciudad, pais, ip_info
            )
            return marcacion, 'Aún no es horario de salida. Marcación registrada en historial.'

        elif en_rango_salida:
            # SALIDA VÁLIDA
            marcacion = _crear_marcacion(
                trabajador, ahora_lim, 'SALIDA_VALIDA', None,
                ip, dispositivo, True,
                latitud, longitud, ciudad, pais, ip_info
            )
            return marcacion, 'Salida registrada correctamente.'

        else:
            # Después de hora_fin_salida (día cerrado)
            marcacion = _crear_marcacion(
                trabajador, ahora_lim, 'FUERA_HORARIO', None,
                ip, dispositivo, False,
                latitud, longitud, ciudad, pais, ip_info
            )
            return marcacion, 'Fuera del horario de salida. Marcación registrada en historial.'


def _crear_marcacion(
    trabajador, fecha, tipo, estado,
    ip, dispositivo, va_a_asistencia,
    latitud, longitud, ciudad, pais, ip_info
):
    """Helper para crear la marcación con todos los campos."""
    return Marcacion.objects.create(
        trabajador      = trabajador,
        fecha           = fecha,
        tipo            = tipo,
        estado          = estado,
        ip              = ip,
        dispositivo     = dispositivo,
        exitoso         = True,
        va_a_asistencia = va_a_asistencia,
        latitud         = latitud  or None,
        longitud        = longitud or None,
        ciudad          = ciudad   or None,
        pais            = pais     or None,
        ip_info         = ip_info  or None,
    )