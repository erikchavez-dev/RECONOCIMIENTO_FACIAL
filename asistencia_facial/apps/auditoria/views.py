"""
Vistas de la API de auditoria 
Permite consultar los registros de auditoria con paginación y filtros
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Auditoria
from .serializers import AuditoriaSerializer
from apps.usuarios.permissions import EsAdmin
from django.db import models as db_models
from django.utils import timezone
import datetime


class AuditoriaListarView(APIView):
    permission_classes = [EsAdmin]

    def get(self, request):
        queryset = Auditoria.objects.select_related('usuario__trabajador').all().order_by('-fecha')

        # Filtro por búsqueda general (usuario, acción, descripción)
        buscar = request.query_params.get('buscar', '')
        if buscar:
            queryset = queryset.filter(
                db_models.Q(accion__icontains=buscar) |
                db_models.Q(descripcion__icontains=buscar) |
                db_models.Q(usuario__username__icontains=buscar) |
                db_models.Q(usuario__trabajador__nombres__icontains=buscar) |
                db_models.Q(usuario__trabajador__apellido_paterno__icontains=buscar)
            )

        # Filtro por tipo de acción
        accion = request.query_params.get('accion', '')
        if accion:
            queryset = queryset.filter(accion__icontains=accion)

        # Filtro por fecha inicio
        fecha_inicio = request.query_params.get('fecha_inicio', '')
        if fecha_inicio:
            try: 
                dt_inicio = datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d')
                dt_inicio = timezone.make_aware(dt_inicio)
                queryset = queryset.filter(fecha__gte=dt_inicio)
            except ValueError:
                pass

        # Filtro por fecha fin
        fecha_fin = request.query_params.get('fecha_fin', '')
        if fecha_fin:
            try:
                dt_fin = datetime.datetime.strptime(fecha_fin, '%Y-%m-%d')
                dt_fin = timezone.make_aware(dt_fin.replace(hour=23, minute=59, second=59))
                queryset = queryset.filter(fecha__lte=dt_fin)
            except ValueError:
                pass

        # Paginación
        pagina    = int(request.query_params.get('pagina', 1))
        por_pagina = 20
        total     = queryset.count()
        inicio    = (pagina - 1) * por_pagina
        fin       = inicio + por_pagina

        auditorias_paginadas = queryset[inicio:fin]
        serializer = AuditoriaSerializer(auditorias_paginadas, many=True)

        return Response({
            'total': total,
            'pagina': pagina,
            'total_paginas': max(1, (total + por_pagina - 1) // por_pagina),
            'por_pagina': por_pagina,
            'auditorias': serializer.data
        }, status=status.HTTP_200_OK)


class AuditoriaUsuarioView(APIView):
    permission_classes = [EsAdmin]

    def get(self, request, usuario_id):
        auditorias = Auditoria.objects.filter(
            usuario_id=usuario_id
        ).order_by('-fecha')
        serializer = AuditoriaSerializer(auditorias, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)