# apps/marcaciones/serializers.py
# Agrega los campos nuevos al serializer existente

from rest_framework import serializers
from django.utils import timezone
from .models import Marcacion


class MarcacionSerializer(serializers.ModelSerializer):
    trabajador_nombre = serializers.SerializerMethodField()
    fecha      = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    ubicacion  = serializers.SerializerMethodField()   # Campo calculado para el admin

    class Meta:
        model  = Marcacion
        fields = [
            'id',
            'trabajador',
            'trabajador_nombre',
            'fecha',
            'tipo',
            'estado',
            'ip',
            'ip_info',
            'dispositivo',
            'exitoso',
            'latitud',
            'longitud',
            'ciudad',
            'pais',
            'ubicacion',
            'created_at',
        ]

    def get_trabajador_nombre(self, obj):
        return f'{obj.trabajador.nombres} {obj.trabajador.apellido_paterno}'

    def get_fecha(self, obj):
        fecha_local = timezone.localtime(obj.fecha)
        return fecha_local.strftime('%Y-%m-%dT%H:%M:%S%z')

    def get_created_at(self, obj):
        fecha_local = timezone.localtime(obj.created_at)
        return fecha_local.strftime('%Y-%m-%dT%H:%M:%S%z')

    def get_ubicacion(self, obj):
        """Devuelve un texto legible de la ubicación para el admin."""
        partes = []
        if obj.ciudad:
            partes.append(obj.ciudad)
        if obj.pais:
            partes.append(obj.pais)
        if not partes and obj.ip:
            partes.append(f'IP: {obj.ip}')
        return ', '.join(partes) if partes else '—'