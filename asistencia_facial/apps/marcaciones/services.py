# apps/marcaciones/services.py
# Actualiza tu función registrar_marcacion para aceptar los nuevos campos.
# Solo se muestra la firma y el fragmento que cambia — el resto queda igual.

from django.utils import timezone
from zoneinfo import ZoneInfo
from .models import Marcacion
from apps.configuracion.models import ConfiguracionSistema
import datetime


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
    Registra una marcación de ENTRADA o SALIDA para el trabajador.
    Incluye validación de horarios (Opción 1: rangos) y datos de geolocalización.
    """
    config = ConfiguracionSistema.objects.first()
    if not config:
        return None, 'No hay configuración del sistema'

    lima_tz   = ZoneInfo('America/Lima')
    ahora     = timezone.now()
    ahora_lim = timezone.localtime(ahora, lima_tz)
    hora_act  = ahora_lim.time()
    hoy       = ahora_lim.date()

    inicio_dia = ahora_lim.replace(hour=0,  minute=0,  second=0,  microsecond=0)
    fin_dia    = ahora_lim.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Marcaciones del día actual para este trabajador
    marcaciones_hoy = Marcacion.objects.filter(
        trabajador=trabajador,
        fecha__gte=inicio_dia,
        fecha__lte=fin_dia,
        exitoso=True,
    )

    entrada_hoy = marcaciones_hoy.filter(tipo='ENTRADA').first()
    salida_hoy  = marcaciones_hoy.filter(tipo='SALIDA').first()

    # Ya marcó entrada Y salida hoy
    if entrada_hoy and salida_hoy:
        return None, 'Ya registró su entrada y salida de hoy'

    # ── LÓGICA DE RANGOS (Opción 1) ─────────────────────────────────────
    en_rango_entrada = config.hora_inicio_entrada <= hora_act <= config.hora_fin_entrada
    # Rango de salida: desde hora_inicio_salida hasta fin del día
    #en_rango_salida  = hora_act >= config.hora_inicio_salida
    en_rango_salida = config.hora_inicio_salida <= hora_act <= config.hora_fin_salida

    # Rango de tardanza: después de hora_fin_entrada pero antes de rango salida
    es_tardanza = hora_act > config.hora_fin_entrada and not en_rango_salida

    if not entrada_hoy:
        # Intentando marcar ENTRADA
        if en_rango_entrada or es_tardanza:
            tipo   = 'ENTRADA'
            estado = 'PUNTUAL' if hora_act <= config.hora_fin_entrada else 'TARDANZA'
        elif en_rango_salida:
            # Llegó en horario de salida sin haber marcado entrada → tardanza extrema
            tipo   = 'ENTRADA'
            estado = 'TARDANZA'
        else:
            return None, 'Fuera del horario de marcación de entrada'

    elif entrada_hoy and not salida_hoy:
        # Intentando marcar SALIDA
        if en_rango_salida:
            tipo   = 'SALIDA'
            estado = None
        else:
            return None, 'Aún no es horario de salida'
    else:
        return None, 'Ya registró su entrada y salida de hoy'

    # ── GUARDAR MARCACIÓN ────────────────────────────────────────────────
    marcacion = Marcacion.objects.create(
        trabajador  = trabajador,
        fecha       = ahora_lim,
        tipo        = tipo,
        estado      = estado,
        ip          = ip,
        dispositivo = dispositivo,
        exitoso     = True,
        # Nuevos campos de geolocalización
        latitud     = latitud  if latitud  else None,
        longitud    = longitud if longitud else None,
        ciudad      = ciudad   or None,
        pais        = pais     or None,
        ip_info     = ip_info  or None,
    )

    return marcacion, None