# apps/marcaciones/ip_service.py
# Servicio para validar IP y obtener info de geolocalización

import ipaddress
import urllib.request
import json
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """
    Obtiene la IP real del cliente considerando proxies y headers comunes.
    """
    # Orden de prioridad para obtener la IP real
    headers_candidatos = [
        'HTTP_X_FORWARDED_FOR',
        'HTTP_X_REAL_IP',
        'HTTP_CF_CONNECTING_IP',   # Cloudflare
        'HTTP_X_CLUSTER_CLIENT_IP',
        'REMOTE_ADDR',
    ]
    for header in headers_candidatos:
        ip = request.META.get(header)
        if ip:
            # X-Forwarded-For puede tener varias IPs separadas por coma
            ip = ip.split(',')[0].strip()
            if ip:
                return ip
    return '0.0.0.0'


def ip_en_rango(ip_cliente: str, rango: str) -> bool:
    """
    Verifica si ip_cliente está dentro del rango dado.
    El rango puede ser:
      - IP exacta:       '192.168.1.10'
      - CIDR:            '192.168.1.0/24'
      - Wildcard simple: '192.168.1.*'
    """
    rango = rango.strip()
    try:
        # Wildcard → convertir a CIDR
        if '*' in rango:
            partes = rango.split('.')
            idx = partes.index('*')
            prefijo = 8 * idx
            rango = '.'.join(p if p != '*' else '0' for p in partes) + f'/{prefijo}'

        red = ipaddress.ip_network(rango, strict=False)
        return ipaddress.ip_address(ip_cliente) in red

    except ValueError:
        # IP exacta como fallback
        return ip_cliente == rango


def validar_ip_autorizada(ip_cliente: str, config) -> tuple[bool, str]:
    """
    Valida si la IP del cliente está autorizada según la configuración.

    Returns:
        (True, '')            → IP autorizada
        (False, 'mensaje')    → IP no autorizada
    """
    # Si el control de IP está desactivado, siempre pasa
    if not config.control_ip_activo:
        return True, ''

    ips_autorizadas = config.get_ips_autorizadas()

    # Si no hay IPs configuradas y el control está activo → bloquear
    if not ips_autorizadas:
        return False, 'No hay IPs autorizadas configuradas. Contacte al administrador.'

    # IPs locales siempre pasan (desarrollo / localhost)
    try:
        ip_obj = ipaddress.ip_address(ip_cliente)
        if ip_obj.is_loopback or ip_obj.is_private:
            # Opcional: descomenta la siguiente línea si quieres bloquear
            # IPs privadas que no estén explícitamente en la lista
            pass  # Por ahora las IPs privadas pasan si están en la red local
    except ValueError:
        pass

    for rango in ips_autorizadas:
        if ip_en_rango(ip_cliente, rango):
            return True, ''

    return False, (
        f'Acceso denegado desde la IP {ip_cliente}. '
        'Solo puede marcar asistencia desde la red autorizada de la Municipalidad.'
    )


def obtener_info_ip(ip: str) -> dict:
    """
    Consulta ipquery.io para obtener información geográfica de la IP.
    Devuelve dict con ciudad, país, región, org.
    Si falla (sin conexión, IP privada, etc.) devuelve dict vacío.

    API gratuita: https://ipquery.io
    No requiere API key para uso básico.
    """
    # IPs privadas / loopback no tienen info geográfica pública
    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_loopback or ip_obj.is_private:
            return {
                'ciudad': 'Red local',
                'pais': 'Local',
                'region': '',
                'org': 'Red interna',
                'isp': '',
            }
    except ValueError:
        pass

    try:
        url = f'https://api.ipquery.io/{ip}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())

        # Estructura de respuesta ipquery.io:
        # { "ip": "...", "location": { "city": "...", "country": "...", ... }, "isp": {...} }
        location = data.get('location', {})
        isp_data = data.get('isp', {})

        return {
            'ciudad':  location.get('city', ''),
            'pais':    location.get('country', ''),
            'region':  location.get('state', ''),
            'org':     isp_data.get('org', ''),
            'isp':     isp_data.get('isp', ''),
        }

    except Exception as e:
        logger.warning(f'No se pudo obtener info de IP {ip}: {e}')
        return {}