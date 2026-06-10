"""
apps/configuracion/models.py

Modelo de configuración del sistema.
Incluye parámetros de geocerca (geofencing) gestionables solo por SUPERADMIN.
"""

from django.db import models


class ConfiguracionSistema(models.Model):
    # ── Horarios ──────────────────────────────────────────────────────────
    hora_inicio_entrada = models.TimeField()
    hora_fin_entrada    = models.TimeField()
    hora_inicio_salida  = models.TimeField()
    hora_fin_salida     = models.TimeField()

    # Minutos de gracia DESPUÉS de hora_fin_entrada para marcar como TARDANZA
    # Si se supera (hora_fin_entrada + tolerancia_minutos) → FUERA_HORARIO
    tolerancia_minutos = models.IntegerField(default=30)

    # ── Seguridad facial / intentos ───────────────────────────────────────
    max_intentos         = models.IntegerField(default=5)
    max_intentos_faciales = models.IntegerField(default=5)
    umbral_similitud     = models.FloatField(default=0.6)

    # ── Control de IP ─────────────────────────────────────────────────────
    # IPs autorizadas separadas por coma. Ej: 127.0.0.1, 192.168.1.0/24
    ip_autorizada    = models.TextField(null=True, blank=True)
    control_ip_activo = models.BooleanField(default=False)

    # ── Geocerca (Geofencing) — solo SUPERADMIN puede modificar ──────────
    # Activa / desactiva toda la validación por geocerca
    geocerca_activa = models.BooleanField(
        default=False,
        help_text='Activa la validación de ubicación por geocerca al marcar asistencia.'
    )
    # Coordenadas del punto central autorizado (sede/oficina)
    geocerca_latitud = models.DecimalField(
        max_digits=10, decimal_places=7,
        null=True, blank=True,
        help_text='Latitud del punto central autorizado (ej: -7.1638000).'
    )
    geocerca_longitud = models.DecimalField(
        max_digits=10, decimal_places=7,
        null=True, blank=True,
        help_text='Longitud del punto central autorizado (ej: -78.5000000).'
    )
    # Radio máximo en metros para considerar la marcación válida
    geocerca_radio_metros = models.IntegerField(
        default=100,
        help_text='Radio en metros dentro del cual se permite marcar (ej: 100).'
    )
    # Si es True y geocerca activa: denegar marcación si no hay coordenadas
    geocerca_obligatoria = models.BooleanField(
        default=True,
        help_text=(
            'Si True y la geocerca está activa: si el usuario deniega permisos '
            'de geolocalización, la marcación es rechazada.'
        )
    )
    # Si es True, registra en auditoría los detalles de cada validación
    geocerca_auditoria = models.BooleanField(
        default=True,
        help_text='Registra en auditoría los detalles de cada validación de geocerca.'
    )

    # ── Metadatos ─────────────────────────────────────────────────────────
    ultima_modificacion_por_id = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='configuraciones_modificadas'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'configuracion_sistema'
        verbose_name = 'Configuración del sistema'
        verbose_name_plural = 'Configuraciones del sistema'

    def __str__(self):
        return f'Configuración #{self.id}'

    def get_ips_autorizadas(self):
        if not self.ip_autorizada:
            return []
        return [ip.strip() for ip in self.ip_autorizada.split(',') if ip.strip()]