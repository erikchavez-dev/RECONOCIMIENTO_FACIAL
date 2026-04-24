from django.db import models
from apps.trabajadores.models import Trabajador


class Marcacion(models.Model):

    TIPO_CHOICES = [
        ('ENTRADA_VALIDA',    'Entrada válida'),
        ('SALIDA_VALIDA',     'Salida válida'),
        ('FUERA_HORARIO',     'Fuera de horario'),
        ('SOLO_VERIFICACION', 'Solo verificación (día no laborable)'),
        # Retrocompatibilidad con registros existentes
        ('ENTRADA', 'Entrada'),
        ('SALIDA',  'Salida'),
    ]

    ESTADO_CHOICES = [
        ('PUNTUAL',  'Puntual'),
        ('TARDANZA', 'Tardanza'),
    ]

    trabajador  = models.ForeignKey(
        Trabajador,
        on_delete=models.PROTECT,
        related_name='marcaciones'
    )
    fecha       = models.DateTimeField()
    tipo        = models.CharField(max_length=20, choices=TIPO_CHOICES)
    estado      = models.CharField(max_length=10, choices=ESTADO_CHOICES, blank=True, null=True)
    ip          = models.CharField(max_length=45, blank=True, null=True)
    dispositivo = models.CharField(max_length=150, blank=True, null=True)
    exitoso     = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    # ── Afecta a la asistencia ──────────────────────────────────
    # True  → se usa para calcular asistencia del día
    # False → solo queda en historial (fuera de horario, día no laborable, etc.)
    va_a_asistencia = models.BooleanField(default=False)

    # ── Geolocalización ──────────────────────────────────────────
    latitud  = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    ciudad   = models.CharField(max_length=100, null=True, blank=True)
    pais     = models.CharField(max_length=100, null=True, blank=True)
    ip_info  = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'marcaciones'
        verbose_name = 'Marcación'
        verbose_name_plural = 'Marcaciones'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.trabajador} - {self.tipo} - {self.fecha}'

    # ── Helper: ¿es una entrada válida (para asistencia)? ────────
    @property
    def es_entrada(self):
        return self.tipo in ('ENTRADA_VALIDA', 'ENTRADA') and self.va_a_asistencia

    # ── Helper: ¿es una salida válida (para asistencia)? ─────────
    @property
    def es_salida(self):
        return self.tipo in ('SALIDA_VALIDA', 'SALIDA') and self.va_a_asistencia