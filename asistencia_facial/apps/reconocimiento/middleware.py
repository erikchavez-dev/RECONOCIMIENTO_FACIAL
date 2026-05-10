from django.http import JsonResponse
from apps.configuracion.models import ConfiguracionSistema
from apps.marcaciones.ip_service import ip_en_rango, get_client_ip


class ControlIPMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Solo aplicar control en endpoints de reconocimiento y marcaciones
        rutas_protegidas = [
            '/api/reconocimiento/verificar/',
            '/api/marcaciones/registrar/',
        ]

        if request.path in rutas_protegidas:
            try:
                config = ConfiguracionSistema.objects.first()

                if config and config.control_ip_activo:
                    ips_autorizadas = config.get_ips_autorizadas()

                    if ips_autorizadas:
                        ip_cliente = get_client_ip(request)

                        # Usar ip_en_rango para soportar IPs exactas,
                        # rangos CIDR (192.168.1.0/24) y wildcards (192.168.1.*)
                        autorizada = any(
                            ip_en_rango(ip_cliente, rango)
                            for rango in ips_autorizadas
                        )

                        if not autorizada:
                            return JsonResponse(
                                {
                                    'error': 'Acceso denegado. Su IP no está autorizada para registrar marcaciones',
                                    'ip': ip_cliente
                                },
                                status=403
                            )
            except Exception:
                pass

        response = self.get_response(request)
        return response