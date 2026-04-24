from django.urls import path
from .views import (
    MarcacionRegistrarView,
    MarcacionHistorialView,
    MarcacionListarView,
    MarcacionHoyView,
    ReporteRangoFechasView,
    ReportePDFView,
    EstadisticasDashboardView,
    AsistenciaResumenView,
    AsistenciaAdminView,
    EditarMarcacionAdminView,
)

urlpatterns = [
    path('', MarcacionListarView.as_view(), name='marcacion-listar'),
    path('registrar/', MarcacionRegistrarView.as_view(), name='marcacion-registrar'),
    path('historial/<int:trabajador_id>/', MarcacionHistorialView.as_view(), name='marcacion-historial'),
    path('hoy/', MarcacionHoyView.as_view(), name='marcacion-hoy'),
    path('reporte/', ReporteRangoFechasView.as_view(), name='marcacion-reporte'),
    path('reporte/pdf/', ReportePDFView.as_view(), name='marcacion-reporte-pdf'),
    path('estadisticas/', EstadisticasDashboardView.as_view(), name='marcacion-estadisticas'),
    path('asistencia/', AsistenciaResumenView.as_view(), name='asistencia-resumen'),
    path('asistencia/admin/', AsistenciaAdminView.as_view(), name='asistencia-admin'),
    path('editar-admin/', EditarMarcacionAdminView.as_view()),
]