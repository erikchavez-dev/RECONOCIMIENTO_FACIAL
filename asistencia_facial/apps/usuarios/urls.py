from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView,
    LogoutView,
    CambiarPasswordView,
    DesbloquearUsuarioView,
    ResetearIntentosFacialesView,
    ListarUsuariosView,
    PerfilView,
    CambiarRolUsuarioView,
    ResetearPasswordView,
    ListarRolesView,
    GestionAdminView,
)

urlpatterns = [
    # Auth
    path('login/',         LoginView.as_view(),         name='login'),
    path('logout/',        LogoutView.as_view(),         name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(),   name='token_refresh'),

    # Perfil & password
    path('perfil/',            PerfilView.as_view(),            name='perfil'),
    path('cambiar-password/',  CambiarPasswordView.as_view(),   name='cambiar_password'),

    # Gestión de usuarios (ADMIN + SUPERADMIN)
    path('listar/',                        ListarUsuariosView.as_view(),        name='listar_usuarios'),
    path('roles/',                         ListarRolesView.as_view(),           name='listar_roles'),
    path('cambiar-rol/<int:pk>/',          CambiarRolUsuarioView.as_view(),     name='cambiar_rol'),
    path('desbloquear/<int:pk>/',          DesbloquearUsuarioView.as_view(),    name='desbloquear_usuario'),
    path('resetear-intentos/<int:pk>/',   ResetearIntentosFacialesView.as_view(), name='resetear_intentos'),
    path('resetear-password/<int:pk>/',   ResetearPasswordView.as_view(),      name='resetear_password'),

    # SUPERADMIN exclusivo: gestión de cuentas ADMIN
    path('gestion-admin/',           GestionAdminView.as_view(), name='promover_admin'),
    path('gestion-admin/<int:pk>/',  GestionAdminView.as_view(), name='degradar_admin'),
]