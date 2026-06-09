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

    def validate(self, data):
        """
        Valida que los horarios sean coherentes:
          1. hora_inicio_entrada < hora_fin_entrada
          2. hora_fin_entrada <= hora_inicio_salida
          3. hora_inicio_salida < hora_fin_salida
        Para PATCH parcial, se fusionan los valores del objeto existente
        con los datos entrantes antes de comparar.
        """
        instance = self.instance  # None en creación, objeto en PATCH

        def get(field):
            # Toma el valor del payload; si no viene (PATCH parcial), usa el actual
            if field in data:
                return data[field]
            if instance:
                return getattr(instance, field, None)
            return None

        hie = get('hora_inicio_entrada')
        hfe = get('hora_fin_entrada')
        his = get('hora_inicio_salida')
        hfs = get('hora_fin_salida')

        # Solo validar si tenemos los cuatro valores
        if all([hie, hfe, his, hfs]):
            if hie >= hfe:
                raise serializers.ValidationError({
                    'hora_fin_entrada': (
                        'La hora fin de entrada debe ser posterior '
                        'a la hora inicio de entrada.'
                    )
                })

            if hfe > his:
                raise serializers.ValidationError({
                    'hora_inicio_salida': (
                        'La hora inicio de salida debe ser posterior '
                        'a la hora fin de entrada.'
                    )
                })

            if his >= hfs:
                raise serializers.ValidationError({
                    'hora_fin_salida': (
                        'La hora fin de salida debe ser posterior '
                        'a la hora inicio de salida.'
                    )
                })

        return data