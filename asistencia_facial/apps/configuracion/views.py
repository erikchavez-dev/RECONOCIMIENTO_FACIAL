"""
apps/configuracion/views.py

Vistas de configuración del sistema.
 - ConfiguracionView        → GET/PATCH para ADMIN y SUPERADMIN (campos generales)
 - ConfiguracionGeocercaView → GET/PATCH exclusivo para SUPERADMIN (campos de geocerca)
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import ConfiguracionSistema
from .serializers import ConfiguracionSistemaSerializer, ConfiguracionGeocercaSerializer
from apps.auditoria.services import registrar_auditoria
from apps.usuarios.permissions import EsAdmin, EsSuperAdmin


class ConfiguracionView(APIView):
    """
    GET  /api/configuracion/  → Lee configuración general (ADMIN / SUPERADMIN)
    PATCH /api/configuracion/ → Modifica configuración general (ADMIN / SUPERADMIN)
    """
    permission_classes = [EsAdmin]

    def get(self, request):
        config = ConfiguracionSistema.objects.first()
        if not config:
            return Response(
                {'error': 'No hay configuración registrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ConfiguracionSistemaSerializer(config)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        config = ConfiguracionSistema.objects.first()
        if not config:
            return Response(
                {'error': 'No hay configuración registrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ConfiguracionSistemaSerializer(
            config,
            data=request.data,
            partial=True
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        try:
            registrar_auditoria(
                usuario=request.user,
                accion='CAMBIO_CONFIGURACION',
                descripcion=f'Se modificó la configuración del sistema: {request.data}',
                ip=request.META.get('REMOTE_ADDR', '0.0.0.0')
            )
        except Exception:
            pass

        return Response(serializer.data, status=status.HTTP_200_OK)


class ConfiguracionGeocercaView(APIView):
    """
    GET  /api/configuracion/geocerca/  → Lee parámetros de geocerca (solo SUPERADMIN)
    PATCH /api/configuracion/geocerca/ → Modifica parámetros de geocerca (solo SUPERADMIN)

    Esta vista está completamente separada de ConfiguracionView para garantizar
    que ningún ADMIN pueda modificar ni ver el estado de la geocerca.
    """
    permission_classes = [EsSuperAdmin]

    def get(self, request):
        config = ConfiguracionSistema.objects.first()
        if not config:
            return Response(
                {'error': 'No hay configuración registrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ConfiguracionGeocercaSerializer(config)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        config = ConfiguracionSistema.objects.first()
        if not config:
            return Response(
                {'error': 'No hay configuración registrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ConfiguracionGeocercaSerializer(
            config,
            data=request.data,
            partial=True
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        # Construir descripción legible para auditoría
        campos_cambiados = list(request.data.keys())
        descripcion = (
            f'SUPERADMIN modificó configuración de geocerca. '
            f'Campos: {", ".join(campos_cambiados)}. '
            f'Valores: {request.data}'
        )

        try:
            registrar_auditoria(
                usuario=request.user,
                accion='CAMBIO_GEOCERCA',
                descripcion=descripcion,
                ip=request.META.get('REMOTE_ADDR', '0.0.0.0')
            )
        except Exception:
            pass

        return Response(serializer.data, status=status.HTTP_200_OK)