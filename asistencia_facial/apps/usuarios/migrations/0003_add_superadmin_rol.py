from django.db import migrations


def crear_rol_superadmin(apps, schema_editor):
    Rol = apps.get_model('usuarios', 'Rol')
    Rol.objects.get_or_create(
        nombre='SUPERADMIN',
        defaults={'descripcion': 'Administrador raíz del sistema. Control total sin restricciones.'}
    )


def eliminar_rol_superadmin(apps, schema_editor):
    Rol = apps.get_model('usuarios', 'Rol')
    Rol.objects.filter(nombre='SUPERADMIN').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_usuario_debe_cambiar_password'),
    ]

    operations = [
        migrations.RunPython(crear_rol_superadmin, eliminar_rol_superadmin),
    ]