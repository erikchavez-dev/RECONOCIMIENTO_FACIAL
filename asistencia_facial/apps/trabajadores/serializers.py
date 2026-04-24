from rest_framework import serializers
from django.utils import timezone
from .models import Trabajador


# Se usa para leer y mostrar datos de un trabajador
class TrabajadorSerializer(serializers.ModelSerializer):
    # Campo calculado: estado real considerando fecha_fin_laboral
    activo_efectivo = serializers.SerializerMethodField()
    # Solo indica si tiene embedding, no expone el vector completo
    embedding = serializers.SerializerMethodField()

    class Meta:
        model = Trabajador
        fields = [
            'id',
            'nombres',
            'apellido_paterno',
            'apellido_materno',
            'dni',
            'telefono',
            'cargo',
            'foto_url',
            'activo',           # estado manual en BD (para el switch)
            'activo_efectivo',  # estado real = activo AND contrato vigente
            'fecha_inicio_laboral',
            'fecha_fin_laboral',
            'fecha_registro',
            'embedding',
        ]

    def get_activo_efectivo(self, obj):
        """
        True solo si:
        1. El trabajador está activo (switch encendido en BD)
        2. La fecha_fin_laboral no ha vencido (o no tiene fecha fin)
        """
        if not obj.activo:
            return False
        if obj.fecha_fin_laboral:
            hoy = timezone.now().date()
            if hoy > obj.fecha_fin_laboral:
                return False
        return True

    def get_embedding(self, obj):
        # Retorna True/False, no el vector completo
        return obj.embedding is not None


# Se usa al crear un nuevo trabajador
class TrabajadorCrearSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trabajador
        fields = [
            'nombres',
            'apellido_paterno',
            'apellido_materno',
            'dni',
            'telefono',
            'cargo',
            'fecha_inicio_laboral',
            'fecha_fin_laboral',
        ]


# Se usa para modificar los datos de un trabajador existente
class TrabajadorActualizarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trabajador
        fields = [
            'nombres',
            'apellido_paterno',
            'apellido_materno',
            'telefono',
            'cargo',
            'fecha_inicio_laboral',
            'fecha_fin_laboral',
            'activo',
        ]