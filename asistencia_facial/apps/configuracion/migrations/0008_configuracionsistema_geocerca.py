"""
Migration 0008: Agrega campos de geocerca (geofencing) a ConfiguracionSistema.
Solo el SUPERADMIN puede gestionar estos parámetros.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracion', '0007_configuracionsistema_tolerancia_minutos'),
    ]

    operations = [
        # ── Activar / desactivar la validación por geocerca ──────────────
        migrations.AddField(
            model_name='configuracionsistema',
            name='geocerca_activa',
            field=models.BooleanField(
                default=False,
                help_text='Activa la validación de ubicación por geocerca al marcar asistencia.'
            ),
        ),
        # ── Latitud de referencia de la sede ─────────────────────────────
        migrations.AddField(
            model_name='configuracionsistema',
            name='geocerca_latitud',
            field=models.DecimalField(
                max_digits=10, decimal_places=7,
                null=True, blank=True,
                help_text='Latitud del punto central autorizado (ej: -7.1638000).'
            ),
        ),
        # ── Longitud de referencia de la sede ────────────────────────────
        migrations.AddField(
            model_name='configuracionsistema',
            name='geocerca_longitud',
            field=models.DecimalField(
                max_digits=10, decimal_places=7,
                null=True, blank=True,
                help_text='Longitud del punto central autorizado (ej: -78.5000000).'
            ),
        ),
        # ── Radio permitido en metros ─────────────────────────────────────
        migrations.AddField(
            model_name='configuracionsistema',
            name='geocerca_radio_metros',
            field=models.IntegerField(
                default=100,
                help_text='Radio en metros dentro del cual se permite marcar (ej: 100).'
            ),
        ),
        # ── ¿Es obligatorio tener ubicación para marcar? ─────────────────
        migrations.AddField(
            model_name='configuracionsistema',
            name='geocerca_obligatoria',
            field=models.BooleanField(
                default=True,
                help_text=(
                    'Si es True y la geocerca está activa: si el usuario deniega '
                    'permisos de geolocalización, la marcación es rechazada.'
                )
            ),
        ),
        # ── ¿Registrar auditoría detallada de cada validación? ───────────
        migrations.AddField(
            model_name='configuracionsistema',
            name='geocerca_auditoria',
            field=models.BooleanField(
                default=True,
                help_text='Si es True, registra en auditoría los detalles de cada validación de geocerca.'
            ),
        ),
    ]