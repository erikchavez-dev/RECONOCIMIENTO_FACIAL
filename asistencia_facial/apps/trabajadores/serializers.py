import re
from rest_framework import serializers
from django.utils import timezone
from .models import Trabajador


# ─────────────────────────────────────────────────────────────────────────────
# Funciones de validación reutilizables
# ─────────────────────────────────────────────────────────────────────────────

def solo_letras(valor, campo='Campo'):
    """Solo letras y espacios (incluye tildes y ñ)."""
    if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-']+", valor.strip()):
        raise serializers.ValidationError(
            f'{campo} solo puede contener letras, espacios y guiones.'
        )
    return valor.strip()


def solo_digitos(valor, longitud_exacta=None, campo='Campo'):
    """Solo dígitos numéricos, con longitud exacta opcional."""
    limpio = valor.strip()
    if not limpio.isdigit():
        raise serializers.ValidationError(
            f'{campo} solo puede contener números.'
        )
    if longitud_exacta and len(limpio) != longitud_exacta:
        raise serializers.ValidationError(
            f'{campo} debe tener exactamente {longitud_exacta} dígitos.'
        )
    return limpio


# ─────────────────────────────────────────────────────────────────────────────
# Serializer de lectura
# ─────────────────────────────────────────────────────────────────────────────

class TrabajadorSerializer(serializers.ModelSerializer):
    activo_efectivo = serializers.SerializerMethodField()
    embedding       = serializers.SerializerMethodField()

    class Meta:
        model  = Trabajador
        fields = [
            'id', 'nombres', 'apellido_paterno', 'apellido_materno',
            'dni', 'telefono', 'cargo', 'foto_url',
            'activo', 'activo_efectivo',
            'fecha_inicio_laboral', 'fecha_fin_laboral',
            'fecha_registro', 'embedding',
        ]

    def get_activo_efectivo(self, obj):
        if not obj.activo:
            return False
        if obj.fecha_fin_laboral:
            if timezone.now().date() > obj.fecha_fin_laboral:
                return False
        return True

    def get_embedding(self, obj):
        return obj.embedding is not None


# ─────────────────────────────────────────────────────────────────────────────
# Serializer de creación
# ─────────────────────────────────────────────────────────────────────────────

class TrabajadorCrearSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Trabajador
        fields = [
            'nombres', 'apellido_paterno', 'apellido_materno',
            'dni', 'telefono', 'cargo',
            'fecha_inicio_laboral', 'fecha_fin_laboral',
        ]

    # ── Validadores de campo ─────────────────────────────────────────────────

    def validate_nombres(self, value):
        return solo_letras(value, 'Nombres')

    def validate_apellido_paterno(self, value):
        return solo_letras(value, 'Apellido paterno')

    def validate_apellido_materno(self, value):
        return solo_letras(value, 'Apellido materno')

    def validate_dni(self, value):
        return solo_digitos(value, longitud_exacta=8, campo='DNI')

    def validate_telefono(self, value):
        if not value:
            return value
        limpio = value.strip()
        # Permite + al inicio (para código de país) y solo dígitos después
        patron = r'^\+?\d{7,15}$'
        if not re.fullmatch(patron, limpio):
            raise serializers.ValidationError(
                'Teléfono inválido. Use solo dígitos (7–15), puede empezar con +.'
            )
        return limpio

    def validate_cargo(self, value):
        if not value:
            return value
        limpio = value.strip()
        # Cargo permite letras, números, espacios y algunos símbolos comunes
        if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s\-\./()]+", limpio):
            raise serializers.ValidationError(
                'Cargo contiene caracteres no permitidos.'
            )
        return limpio

    def validate(self, data):
        """Validación cruzada de fechas."""
        inicio = data.get('fecha_inicio_laboral')
        fin    = data.get('fecha_fin_laboral')
        if inicio and fin and fin < inicio:
            raise serializers.ValidationError(
                {'fecha_fin_laboral': 'La fecha fin no puede ser anterior a la fecha de inicio.'}
            )
        return data


# ─────────────────────────────────────────────────────────────────────────────
# Serializer de actualización (igual que crear, pero sin DNI)
# ─────────────────────────────────────────────────────────────────────────────

class TrabajadorActualizarSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Trabajador
        fields = [
            'nombres', 'apellido_paterno', 'apellido_materno',
            'telefono', 'cargo',
            'fecha_inicio_laboral', 'fecha_fin_laboral',
            'activo',
        ]

    def validate_nombres(self, value):
        return solo_letras(value, 'Nombres')

    def validate_apellido_paterno(self, value):
        return solo_letras(value, 'Apellido paterno')

    def validate_apellido_materno(self, value):
        return solo_letras(value, 'Apellido materno')

    def validate_telefono(self, value):
        if not value:
            return value
        limpio = value.strip()
        if not re.fullmatch(r'^\+?\d{7,15}$', limpio):
            raise serializers.ValidationError(
                'Teléfono inválido. Use solo dígitos (7–15), puede empezar con +.'
            )
        return limpio

    def validate_cargo(self, value):
        if not value:
            return value
        limpio = value.strip()
        if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9\s\-\./()]+", limpio):
            raise serializers.ValidationError(
                'Cargo contiene caracteres no permitidos.'
            )
        return limpio

    def validate(self, data):
        inicio = data.get('fecha_inicio_laboral')
        fin    = data.get('fecha_fin_laboral')
        if inicio and fin and fin < inicio:
            raise serializers.ValidationError(
                {'fecha_fin_laboral': 'La fecha fin no puede ser anterior a la fecha de inicio.'}
            )
        return data