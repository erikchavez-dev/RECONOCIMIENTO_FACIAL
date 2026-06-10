from rest_framework import serializers
from .models import ConfiguracionSistema


class ConfiguracionSistemaSerializer(serializers.ModelSerializer):
    """
    Configuración general del sistema.
    Accesible por ADMIN y SUPERADMIN.
    No expone campos de geocerca.
    """

    class Meta:
        model = ConfiguracionSistema
        fields = [
            'id',
            'hora_inicio_entrada',
            'hora_fin_entrada',
            'hora_inicio_salida',
            'hora_fin_salida',
            'tolerancia_minutos',
            'max_intentos',
            'max_intentos_faciales',
            'umbral_similitud',
            'ip_autorizada',
            'control_ip_activo',
            'created_at',
        ]

    def validate(self, data):
        """
        Valida que los horarios sean coherentes:

        1. hora_inicio_entrada < hora_fin_entrada
        2. hora_fin_entrada <= hora_inicio_salida
        3. hora_inicio_salida < hora_fin_salida

        Compatible con PATCH parcial.
        """
        instance = self.instance

        def get(field):
            if field in data:
                return data[field]

            if instance:
                return getattr(instance, field, None)

            return None

        hie = get('hora_inicio_entrada')
        hfe = get('hora_fin_entrada')
        his = get('hora_inicio_salida')
        hfs = get('hora_fin_salida')

        if all([hie, hfe, his, hfs]):

            if hie >= hfe:
                raise serializers.ValidationError({
                    'hora_fin_entrada':
                        'La hora fin de entrada debe ser posterior '
                        'a la hora inicio de entrada.'
                })

            if hfe > his:
                raise serializers.ValidationError({
                    'hora_inicio_salida':
                        'La hora inicio de salida debe ser posterior '
                        'a la hora fin de entrada.'
                })

            if his >= hfs:
                raise serializers.ValidationError({
                    'hora_fin_salida':
                        'La hora fin de salida debe ser posterior '
                        'a la hora inicio de salida.'
                })

        return data


class ConfiguracionGeocercaSerializer(serializers.ModelSerializer):
    """
    Configuración exclusiva de geocerca.
    Solo SUPERADMIN.
    """

    class Meta:
        model = ConfiguracionSistema
        fields = [
            'id',
            'geocerca_activa',
            'geocerca_latitud',
            'geocerca_longitud',
            'geocerca_radio_metros',
            'geocerca_obligatoria',
            'geocerca_auditoria',
        ]

    def validate(self, data):
        """
        Validaciones de geocerca.
        Compatible con PATCH parcial.
        """
        activa = data.get(
            'geocerca_activa',
            getattr(self.instance, 'geocerca_activa', False)
        )

        latitud = data.get(
            'geocerca_latitud',
            getattr(self.instance, 'geocerca_latitud', None)
        )

        longitud = data.get(
            'geocerca_longitud',
            getattr(self.instance, 'geocerca_longitud', None)
        )

        if activa and (latitud is None or longitud is None):
            raise serializers.ValidationError(
                'Para activar la geocerca debe configurar latitud y longitud.'
            )

        radio = data.get(
            'geocerca_radio_metros',
            getattr(self.instance, 'geocerca_radio_metros', 100)
        )

        if radio is not None and radio < 10:
            raise serializers.ValidationError(
                'El radio mínimo permitido es 10 metros.'
            )

        if radio is not None and radio > 10000:
            raise serializers.ValidationError(
                'El radio máximo permitido es 10000 metros.'
            )

        return data