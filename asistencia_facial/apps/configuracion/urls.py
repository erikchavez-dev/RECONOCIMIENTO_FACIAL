"""
apps/configuracion/urls.py

REEMPLAZAR el archivo actual con este contenido.
Agrega el endpoint exclusivo de geocerca para SUPERADMIN.
"""

from django.urls import path
from .views import ConfiguracionView, ConfiguracionGeocercaView

urlpatterns = [
    # Configuración general — ADMIN y SUPERADMIN
    path('', ConfiguracionView.as_view(), name='configuracion'),

    # Geocerca — exclusivo SUPERADMIN
    path('geocerca/', ConfiguracionGeocercaView.as_view(), name='configuracion-geocerca'),
]