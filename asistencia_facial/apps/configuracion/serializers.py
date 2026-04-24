from rest_framework import serializers
from .models import ConfiguracionSistema


class ConfiguracionSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionSistema
        fields = [
            'id',
            'hora_inicio_entrada',
            'hora_fin_entrada',
            'hora_inicio_salida',
            'hora_fin_salida',
            'tolerancia_minutos',      # ← AGREGADO
            'max_intentos',
            'max_intentos_faciales',
            'umbral_similitud',
            'ip_autorizada',
            'control_ip_activo',
            'created_at',
        ]