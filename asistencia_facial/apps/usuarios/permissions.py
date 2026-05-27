from rest_framework.permissions import BasePermission


class EsSuperAdmin(BasePermission):
    """Solo el SUPERADMIN puede acceder."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.rol.nombre == 'SUPERADMIN')


class EsAdmin(BasePermission):
    """ADMIN o SUPERADMIN pueden acceder."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.rol.nombre in ['ADMIN', 'SUPERADMIN'])


class EsSoloAdmin(BasePermission):
    """Solo el ADMIN (sin SUPERADMIN). Usado en endpoints que el SUPERADMIN gestiona diferente."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.rol.nombre == 'ADMIN')


class EsTrabajador(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.rol.nombre == 'TRABAJADOR')


class EsAdminOTrabajador(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.rol.nombre in ['ADMIN', 'SUPERADMIN', 'TRABAJADOR'])