from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer
from .services import validar_login
from .models import Usuario, Rol
from apps.trabajadores.models import Trabajador
from apps.auditoria.services import registrar_auditoria
from django.contrib.auth.hashers import make_password
from apps.usuarios.permissions import EsAdmin, EsSuperAdmin
from math import ceil
from django.db.models import Q


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

JERARQUIA_ROLES = {'TRABAJADOR': 0, 'ADMIN': 1, 'SUPERADMIN': 2}


def _nivel(rol_nombre):
    return JERARQUIA_ROLES.get(rol_nombre, -1)


def get_tokens_for_user(usuario):
    refresh = RefreshToken()
    refresh['user_id']        = usuario.id
    refresh['username']       = usuario.username
    refresh['rol']            = usuario.rol.nombre
    refresh['nombre_completo'] = f'{usuario.trabajador.nombres} {usuario.trabajador.apellido_paterno}'

    access = refresh.access_token
    access['user_id']         = usuario.id
    access['username']        = usuario.username
    access['rol']             = usuario.rol.nombre
    access['nombre_completo'] = f'{usuario.trabajador.nombres} {usuario.trabajador.apellido_paterno}'

    return refresh, access


def _get_client_ip(request):
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


# ─────────────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────────────

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        ip       = _get_client_ip(request)

        usuario, error = validar_login(username, password)
        if error:
            try:
                u = Usuario.objects.get(username=username)
                registrar_auditoria(u, 'LOGIN_FALLIDO', f'Intento fallido: {error}', ip)
            except Usuario.DoesNotExist:
                pass
            return Response({'error': error}, status=status.HTTP_401_UNAUTHORIZED)

        registrar_auditoria(usuario, 'LOGIN_EXITOSO', 'Inicio de sesión exitoso', ip)
        refresh, access = get_tokens_for_user(usuario)

        return Response({
            'access':  str(access),
            'refresh': str(refresh),
            'debe_cambiar_password': usuario.debe_cambiar_password,
            'usuario': {
                'id':             usuario.id,
                'username':       usuario.username,
                'rol':            usuario.rol.nombre,
                'nombre_completo': f'{usuario.trabajador.nombres} {usuario.trabajador.apellido_paterno}',
                'trabajador_id':  usuario.trabajador.id,
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
            try:
                registrar_auditoria(request.user, 'LOGOUT', 'Cierre de sesión', _get_client_ip(request))
            except Exception:
                pass
            return Response({'mensaje': 'Sesión cerrada correctamente'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)


class CambiarPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password_actual = request.data.get('password_actual')
        password_nueva  = request.data.get('password_nueva')
        ip              = _get_client_ip(request)

        if not password_actual or not password_nueva:
            return Response({'error': 'password_actual y password_nueva son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

        if len(password_nueva) < 6:
            return Response({'error': 'La nueva contraseña debe tener mínimo 6 caracteres'}, status=status.HTTP_400_BAD_REQUEST)

        usuario = request.user
        if not usuario.check_password(password_actual):
            registrar_auditoria(usuario, 'CAMBIO_PASSWORD_FALLIDO', 'Contraseña actual incorrecta', ip)
            return Response({'error': 'La contraseña actual es incorrecta'}, status=status.HTTP_400_BAD_REQUEST)

        usuario.password = make_password(password_nueva)
        usuario.debe_cambiar_password = False
        usuario.save()

        registrar_auditoria(usuario, 'CAMBIO_PASSWORD', 'Contraseña actualizada correctamente', ip)
        return Response({'mensaje': 'Contraseña actualizada correctamente'}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────────────────
# Perfil
# ─────────────────────────────────────────────────────────────────────────────

class PerfilView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({
            'id':               u.id,
            'username':         u.username,
            'rol':              u.rol.nombre,
            'nombre_completo':  f'{u.trabajador.nombres} {u.trabajador.apellido_paterno} {u.trabajador.apellido_materno}',
            'dni':              u.trabajador.dni,
            'cargo':            u.trabajador.cargo,
            'trabajador_id':    u.trabajador.id,
            'foto_url':         u.trabajador.foto_url,
            'debe_cambiar_password': u.debe_cambiar_password,
            'bloqueado':        u.bloqueado,
        }, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────────────────
# Listar usuarios
# ─────────────────────────────────────────────────────────────────────────────

class ListarUsuariosView(APIView):
    permission_classes = [EsAdmin]

    def get(self, request):
        buscar = request.GET.get('buscar', '')
        pagina = int(request.GET.get('pagina', 1))
        limite = int(request.GET.get('limite', 6))

        mi_rol = request.user.rol.nombre

        # SUPERADMIN ve todos; ADMIN no ve SUPERADMIN
        if mi_rol == 'SUPERADMIN':
            usuarios = Usuario.objects.select_related('trabajador', 'rol').all()
        else:
            usuarios = Usuario.objects.select_related('trabajador', 'rol').exclude(rol__nombre='SUPERADMIN')

        if buscar:
            usuarios = usuarios.filter(
                Q(trabajador__dni__icontains=buscar) |
                Q(trabajador__nombres__icontains=buscar) |
                Q(trabajador__apellido_paterno__icontains=buscar)
            )

        total   = usuarios.count()
        inicio  = (pagina - 1) * limite
        usuarios = usuarios.order_by('trabajador__apellido_paterno')[inicio:inicio + limite]

        data = [{
            'id':               u.id,
            'username':         u.username,
            'rol':              u.rol.nombre,
            'nombre_completo':  f'{u.trabajador.nombres} {u.trabajador.apellido_paterno} {u.trabajador.apellido_materno}',
            'dni':              u.trabajador.dni,
            'cargo':            u.trabajador.cargo,
            'activo':           u.trabajador.activo,
            'bloqueado':        u.bloqueado,
            'intentos_fallidos': u.intentos_fallidos,
            'debe_cambiar_password': u.debe_cambiar_password,
            'ultimo_login':     u.ultimo_login,
        } for u in usuarios]

        return Response({
            'total':        total,
            'pagina':       pagina,
            'total_paginas': ceil(total / limite),
            'usuarios':     data,
        }, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────────────────
# Cambiar rol  —  reglas de jerarquía
# ─────────────────────────────────────────────────────────────────────────────

class CambiarRolUsuarioView(APIView):
    permission_classes = [EsAdmin]

    def patch(self, request, pk):
        ip       = _get_client_ip(request)
        mi_rol   = request.user.rol.nombre
        mi_nivel = _nivel(mi_rol)

        try:
            usuario_objetivo = Usuario.objects.select_related('rol').get(pk=pk)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # No puede modificarse a sí mismo
        if usuario_objetivo.id == request.user.id:
            return Response({'error': 'No puedes cambiar tu propio rol'}, status=status.HTTP_403_FORBIDDEN)

        # ADMIN no puede tocar a otro ADMIN ni a SUPERADMIN
        if mi_rol == 'ADMIN' and _nivel(usuario_objetivo.rol.nombre) >= _nivel('ADMIN'):
            return Response(
                {'error': 'No tienes permiso para modificar el rol de este usuario'},
                status=status.HTTP_403_FORBIDDEN
            )

        rol_nombre = request.data.get('rol')
        if not rol_nombre:
            return Response({'error': 'rol es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        # ADMIN no puede asignar SUPERADMIN ni otro ADMIN
        if mi_rol == 'ADMIN' and _nivel(rol_nombre) >= _nivel('ADMIN'):
            return Response(
                {'error': 'No tienes permiso para asignar ese rol'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            nuevo_rol = Rol.objects.get(nombre=rol_nombre)
        except Rol.DoesNotExist:
            return Response({'error': 'Rol no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        rol_anterior = usuario_objetivo.rol.nombre
        usuario_objetivo.rol = nuevo_rol
        usuario_objetivo.save()

        registrar_auditoria(
            request.user, 'CAMBIO_ROL',
            f'Rol de {usuario_objetivo.username} cambiado de {rol_anterior} → {rol_nombre}',
            ip
        )

        return Response({'mensaje': f'Rol actualizado a {rol_nombre}'}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────────────────
# Desbloquear / resetear intentos
# ─────────────────────────────────────────────────────────────────────────────

class DesbloquearUsuarioView(APIView):
    permission_classes = [EsAdmin]

    def post(self, request, pk):
        ip = _get_client_ip(request)
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # ADMIN no puede desbloquear a SUPERADMIN ni a otro ADMIN
        if request.user.rol.nombre == 'ADMIN' and _nivel(usuario.rol.nombre) >= _nivel('ADMIN'):
            return Response({'error': 'No tienes permiso para desbloquear a este usuario'}, status=status.HTTP_403_FORBIDDEN)

        usuario.bloqueado        = False
        usuario.intentos_fallidos = 0
        usuario.save()

        registrar_auditoria(request.user, 'DESBLOQUEAR_USUARIO', f'Usuario {usuario.username} desbloqueado', ip)
        return Response({'mensaje': f'Usuario {usuario.username} desbloqueado correctamente'}, status=status.HTTP_200_OK)


class ResetearIntentosFacialesView(APIView):
    permission_classes = [EsAdmin]

    def post(self, request, pk):
        ip = _get_client_ip(request)
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.rol.nombre == 'ADMIN' and _nivel(usuario.rol.nombre) >= _nivel('ADMIN'):
            return Response({'error': 'No tienes permiso para resetear los intentos de este usuario'}, status=status.HTTP_403_FORBIDDEN)

        usuario.intentos_fallidos = 0
        usuario.bloqueado          = False
        usuario.save()

        registrar_auditoria(request.user, 'RESETEAR_INTENTOS_FACIALES', f'Intentos faciales reseteados para {usuario.username}', ip)
        return Response({'mensaje': f'Intentos faciales reseteados para {usuario.username}'}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────────────────
# Resetear password
# ─────────────────────────────────────────────────────────────────────────────

class ResetearPasswordView(APIView):
    permission_classes = [EsAdmin]

    def post(self, request, pk):
        ip = _get_client_ip(request)
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # ADMIN no puede resetear password de ADMIN o SUPERADMIN
        if request.user.rol.nombre == 'ADMIN' and _nivel(usuario.rol.nombre) >= _nivel('ADMIN'):
            return Response({'error': 'No tienes permiso para resetear la contraseña de este usuario'}, status=status.HTTP_403_FORBIDDEN)

        usuario.password             = make_password('municipalidad2026')
        usuario.debe_cambiar_password = True
        usuario.save()

        registrar_auditoria(request.user, 'RESETEAR_PASSWORD', f'Contraseña reseteada para {usuario.username}', ip)
        return Response({'mensaje': 'Contraseña reseteada a municipalidad2026'}, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────────────────
# Listar roles disponibles  (útil para el frontend al asignar roles)
# ─────────────────────────────────────────────────────────────────────────────

class ListarRolesView(APIView):
    permission_classes = [EsAdmin]

    def get(self, request):
        mi_rol = request.user.rol.nombre
        roles  = Rol.objects.all()

        # ADMIN solo puede ver los roles que puede asignar (no ADMIN, no SUPERADMIN)
        if mi_rol == 'ADMIN':
            roles = roles.exclude(nombre__in=['ADMIN', 'SUPERADMIN'])

        data = [{'id': r.id, 'nombre': r.nombre, 'descripcion': r.descripcion} for r in roles]
        return Response(data, status=status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────────────────
# SUPERADMIN exclusivo: gestión de cuentas ADMIN
# ─────────────────────────────────────────────────────────────────────────────

class GestionAdminView(APIView):
    """Solo SUPERADMIN puede crear/modificar cuentas ADMIN."""
    permission_classes = [EsSuperAdmin]

    def post(self, request):
        """Promover un TRABAJADOR existente a ADMIN."""
        ip           = _get_client_ip(request)
        usuario_id   = request.data.get('usuario_id')

        if not usuario_id:
            return Response({'error': 'usuario_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            usuario = Usuario.objects.select_related('rol').get(pk=usuario_id)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if usuario.rol.nombre == 'SUPERADMIN':
            return Response({'error': 'No se puede modificar a otro SUPERADMIN'}, status=status.HTTP_403_FORBIDDEN)

        try:
            rol_admin = Rol.objects.get(nombre='ADMIN')
        except Rol.DoesNotExist:
            return Response({'error': 'Rol ADMIN no existe en la base de datos'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        rol_anterior  = usuario.rol.nombre
        usuario.rol   = rol_admin
        usuario.save()

        registrar_auditoria(
            request.user, 'PROMOVER_A_ADMIN',
            f'{usuario.username} promovido de {rol_anterior} a ADMIN',
            ip
        )
        return Response({'mensaje': f'{usuario.username} ahora es ADMIN'}, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """Degradar un ADMIN a TRABAJADOR."""
        ip = _get_client_ip(request)
        if not pk:
            return Response({'error': 'pk es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            usuario = Usuario.objects.select_related('rol').get(pk=pk)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if usuario.rol.nombre != 'ADMIN':
            return Response({'error': 'El usuario no es ADMIN'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rol_trabajador = Rol.objects.get(nombre='TRABAJADOR')
        except Rol.DoesNotExist:
            return Response({'error': 'Rol TRABAJADOR no existe'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        usuario.rol = rol_trabajador
        usuario.save()

        registrar_auditoria(
            request.user, 'DEGRADAR_ADMIN',
            f'{usuario.username} degradado de ADMIN a TRABAJADOR',
            ip
        )
        return Response({'mensaje': f'{usuario.username} ahora es TRABAJADOR'}, status=status.HTTP_200_OK)