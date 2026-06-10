"""
apps/marcaciones/geo_service.py

Servicio de validación por geocerca (Geofencing).
Usa la fórmula de Haversine para calcular distancia real en metros
entre las coordenadas del dispositivo y el punto de referencia configurado.

Este módulo es invocado desde MarcacionRegistrarView ANTES de llamar
a registrar_marcacion(), por lo que puede rechazar la marcación sin
que se cree ningún registro en la tabla de marcaciones.
"""

import math
import logging
from django.utils import timezone
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Constante: radio de la Tierra en metros
# ─────────────────────────────────────────────────────────────────────────────
RADIO_TIERRA_M = 6_371_000


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula la distancia en metros entre dos puntos geográficos
    usando la fórmula de Haversine.

    Args:
        lat1, lon1: Coordenadas del dispositivo del usuario.
        lat2, lon2: Coordenadas de referencia (sede configurada).

    Returns:
        Distancia en metros (float).
    """
    # Convertir grados a radianes
    phi1    = math.radians(lat1)
    phi2    = math.radians(lat2)
    dphi    = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (math.sin(dphi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return RADIO_TIERRA_M * c


def validar_geocerca(
    latitud,
    longitud,
    config,
    ip: str,
    dispositivo: str,
    navegador: str = '',
) -> tuple[bool, str, dict]:
    """
    Valida si las coordenadas recibidas están dentro del radio autorizado.

    Args:
        latitud:    Latitud reportada por el dispositivo (puede ser None).
        longitud:   Longitud reportada por el dispositivo (puede ser None).
        config:     Instancia de ConfiguracionSistema.
        ip:         IP del cliente (para auditoría).
        dispositivo: User-agent o descripción del dispositivo.
        navegador:  Navegador detectado (para auditoría).

    Returns:
        Tuple (permitido: bool, mensaje: str, auditoria_data: dict)
         - permitido=True  → la marcación puede continuar.
         - permitido=False → la marcación debe ser rechazada.
         - auditoria_data  → dict con todos los campos de auditoría.
    """
    lima_tz   = ZoneInfo('America/Lima')
    ahora_str = timezone.localtime(timezone.now(), lima_tz).strftime('%Y-%m-%dT%H:%M:%S')

    # ── Caso 1: Geocerca desactivada → siempre permitir ──────────────────
    if not config.geocerca_activa:
        return True, '', {}

    # ── Caso 2: No se recibieron coordenadas ─────────────────────────────
    if latitud is None or longitud is None:
        if config.geocerca_obligatoria:
            auditoria = _build_auditoria(
                lat_disp=None,
                lon_disp=None,
                distancia=None,
                ip=ip,
                dispositivo=dispositivo,
                navegador=navegador,
                fecha=ahora_str,
                resultado='RECHAZADO',
                motivo='No se recibieron coordenadas del dispositivo (permisos denegados o GPS no disponible).',
            )
            return (
                False,
                'La validación de ubicación es obligatoria. '
                'Por favor, permite el acceso a tu ubicación e intenta nuevamente.',
                auditoria,
            )
        else:
            # No es obligatoria → dejar pasar sin validar ubicación
            return True, '', {}

    # ── Caso 3: El sistema no tiene configuradas las coordenadas de referencia
    if config.geocerca_latitud is None or config.geocerca_longitud is None:
        logger.error(
            'Geocerca activa pero sin coordenadas de referencia configuradas. '
            'Contacte al SUPERADMIN.'
        )
        auditoria = _build_auditoria(
            lat_disp=float(latitud),
            lon_disp=float(longitud),
            distancia=None,
            ip=ip,
            dispositivo=dispositivo,
            navegador=navegador,
            fecha=ahora_str,
            resultado='RECHAZADO',
            motivo='Geocerca activa pero sin punto de referencia configurado.',
        )
        return (
            False,
            'Error de configuración: la geocerca está activa pero no tiene '
            'punto de referencia. Contacte al administrador.',
            auditoria,
        )

    # ── Caso 4: Calcular distancia con Haversine ─────────────────────────
    lat_disp = float(latitud)
    lon_disp = float(longitud)
    lat_ref  = float(config.geocerca_latitud)
    lon_ref  = float(config.geocerca_longitud)
    radio    = config.geocerca_radio_metros

    distancia = haversine(lat_disp, lon_disp, lat_ref, lon_ref)
    distancia_redondeada = round(distancia, 2)

    if distancia <= radio:
        # Dentro del radio → marcación autorizada
        auditoria = _build_auditoria(
            lat_disp=lat_disp,
            lon_disp=lon_disp,
            distancia=distancia_redondeada,
            ip=ip,
            dispositivo=dispositivo,
            navegador=navegador,
            fecha=ahora_str,
            resultado='APROBADO',
            motivo=f'Dentro del radio autorizado ({distancia_redondeada}m ≤ {radio}m).',
        )
        return True, '', auditoria
    else:
        # Fuera del radio → marcación rechazada
        exceso = round(distancia - radio, 2)
        auditoria = _build_auditoria(
            lat_disp=lat_disp,
            lon_disp=lon_disp,
            distancia=distancia_redondeada,
            ip=ip,
            dispositivo=dispositivo,
            navegador=navegador,
            fecha=ahora_str,
            resultado='RECHAZADO',
            motivo=(
                f'Fuera del área autorizada. '
                f'Distancia: {distancia_redondeada}m, '
                f'Radio permitido: {radio}m, '
                f'Excede por: {exceso}m.'
            ),
        )
        return (
            False,
            f'Marcación rechazada: te encuentras fuera del área autorizada '
            f'({distancia_redondeada:.0f}m de distancia, radio permitido: {radio}m). '
            f'Solo puedes marcar asistencia desde las instalaciones.',
            auditoria,
        )


def _build_auditoria(
    lat_disp,
    lon_disp,
    distancia,
    ip,
    dispositivo,
    navegador,
    fecha,
    resultado,
    motivo,
) -> dict:
    """Construye el dict de auditoría de geocerca."""
    return {
        'latitud_reportada':  lat_disp,
        'longitud_reportada': lon_disp,
        'distancia_metros':   distancia,
        'ip':                 ip,
        'dispositivo':        dispositivo,
        'navegador':          navegador,
        'fecha_hora':         fecha,
        'resultado':          resultado,
        'motivo':             motivo,
    }