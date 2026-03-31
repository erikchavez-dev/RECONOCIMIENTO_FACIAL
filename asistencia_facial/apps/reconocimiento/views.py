# reconocimiento/views.py — con validación IP + geolocalización

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from apps.trabajadores.models import Trabajador
from apps.marcaciones.services import registrar_marcacion
from apps.marcaciones.ip_service import get_client_ip, validar_ip_autorizada, obtener_info_ip
from apps.configuracion.models import ConfiguracionSistema
from apps.usuarios.models import Usuario
from apps.auditoria.services import registrar_auditoria
from .services import generar_embedding, generar_embedding_promedio, comparar_embeddings
from apps.usuarios.permissions import EsAdmin
import logging

logger = logging.getLogger(__name__)


class RegistrarEmbeddingView(APIView):
    permission_classes = [EsAdmin]

    def post(self, request):
        trabajador_id   = request.data.get('trabajador_id')
        imagen_base64   = request.data.get('imagen')
        imagenes_base64 = request.data.get('imagenes')

        if not trabajador_id:
            return Response({'error': 'trabajador_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        if not imagen_base64 and not imagenes_base64:
            return Response({'error': 'Se requiere imagen o imagenes'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            trabajador = Trabajador.objects.get(pk=trabajador_id)
        except Trabajador.DoesNotExist:
            return Response({'error': 'Trabajador no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if imagenes_base64:
            if not isinstance(imagenes_base64, list):
                return Response({'error': 'imagenes debe ser una lista'}, status=status.HTTP_400_BAD_REQUEST)
            embedding, error = generar_embedding_promedio(imagenes_base64)
            metodo = 'promedio'
        else:
            embedding, error = generar_embedding(imagen_base64)
            metodo = 'simple'

        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        trabajador.embedding = embedding
        trabajador.embedding_actualizado = timezone.now()
        trabajador.save()

        try:
            registrar_auditoria(
                usuario=request.user,
                accion='REGISTRAR_EMBEDDING',
                descripcion=f'Embedding registrado para {trabajador.nombres} {trabajador.apellido_paterno} (método: {metodo})',
                ip=get_client_ip(request)
            )
        except Exception:
            pass

        return Response({
            'mensaje': 'Embedding registrado correctamente',
            'metodo': metodo,
            'imagenes_procesadas': len(imagenes_base64) if imagenes_base64 else 1
        }, status=status.HTTP_200_OK)


class VerificarRostroView(APIView):

    def post(self, request):
        trabajador_id = request.data.get('trabajador_id')
        imagen_base64 = request.data.get('imagen')
        dispositivo   = request.data.get('dispositivo', 'No especificado')

        # Geolocalización enviada desde el frontend (opcional)
        latitud  = request.data.get('latitud')
        longitud = request.data.get('longitud')

        if not trabajador_id or not imagen_base64:
            return Response(
                {'error': 'trabajador_id e imagen son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            trabajador = Trabajador.objects.get(pk=trabajador_id)
        except Trabajador.DoesNotExist:
            return Response({'error': 'Trabajador no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if not trabajador.activo:
            return Response({'error': 'Trabajador inactivo'}, status=status.HTTP_403_FORBIDDEN)

        if not trabajador.embedding:
            return Response({'error': 'El trabajador no tiene embedding registrado'}, status=status.HTTP_400_BAD_REQUEST)

        config = ConfiguracionSistema.objects.first()
        if not config:
            return Response({'error': 'No hay configuración del sistema registrada'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            usuario = Usuario.objects.get(trabajador=trabajador)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if usuario.bloqueado:
            return Response(
                {'error': 'Usuario bloqueado. Contacte al administrador'},
                status=status.HTTP_403_FORBIDDEN
            )

        # ── VALIDACIÓN DE IP ──────────────────────────────────────────────
        ip = get_client_ip(request)
        ip_ok, ip_error = validar_ip_autorizada(ip, config)

        if not ip_ok:
            registrar_auditoria(
                usuario=usuario,
                accion='ACCESO_IP_DENEGADO',
                descripcion=f'Intento de marcación desde IP no autorizada: {ip}',
                ip=ip
            )
            return Response({'error': ip_error}, status=status.HTTP_403_FORBIDDEN)

        # ── RECONOCIMIENTO FACIAL ─────────────────────────────────────────
        embedding_capturado, error = generar_embedding(imagen_base64)
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        verificado, similitud = comparar_embeddings(
            embedding_capturado,
            trabajador.embedding,
            config.umbral_similitud
        )

        if not verificado:
            usuario.intentos_fallidos += 1
            if usuario.intentos_fallidos >= config.max_intentos_faciales:
                usuario.bloqueado = True
                usuario.save()
                registrar_auditoria(
                    usuario=usuario,
                    accion='VERIFICACION_FALLIDA',
                    descripcion=f'Usuario bloqueado por intentos faciales. Similitud: {similitud:.2f}. IP: {ip}',
                    ip=ip
                )
                return Response(
                    {'error': 'Usuario bloqueado por intentos faciales fallidos'},
                    status=status.HTTP_403_FORBIDDEN
                )
            usuario.save()
            registrar_auditoria(
                usuario=usuario,
                accion='VERIFICACION_FALLIDA',
                descripcion=f'Rostro no verificado. Similitud: {similitud:.2f}. Intentos: {usuario.intentos_fallidos}. IP: {ip}',
                ip=ip
            )
            restantes = config.max_intentos_faciales - usuario.intentos_fallidos
            return Response({
                'error': f'El rostro no coincide con el trabajador registrado. Intentos restantes: {restantes}',
                'similitud': round(similitud, 2),
                'intentos_restantes': restantes
            }, status=status.HTTP_401_UNAUTHORIZED)

        # ── VERIFICACIÓN EXITOSA ──────────────────────────────────────────
        usuario.intentos_fallidos = 0
        usuario.save()

        # Obtener info geográfica de la IP (no bloquea si falla)
        info_ip = obtener_info_ip(ip)
        ciudad = info_ip.get('ciudad', '')
        pais   = info_ip.get('pais', '')
        ip_info_str = f"{info_ip.get('org', '')} / {info_ip.get('isp', '')}".strip(' /')

        # Registrar marcación con datos de geolocalización
        marcacion, error = registrar_marcacion(
            trabajador, ip, dispositivo,
            latitud=latitud,
            longitud=longitud,
            ciudad=ciudad,
            pais=pais,
            ip_info=ip_info_str or None,
        )
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        registrar_auditoria(
            usuario=usuario,
            accion='MARCACION_EXITOSA',
            descripcion=(
                f'Marcación {marcacion.tipo} registrada. '
                f'Estado: {marcacion.estado}. '
                f'Similitud: {similitud:.2f}. '
                f'IP: {ip}. '
                f'Ubicación: {ciudad}, {pais}'
            ),
            ip=ip
        )

        return Response({
            'mensaje': 'Verificación exitosa',
            'similitud': similitud,
            'marcacion': {
                'id':     marcacion.id,
                'tipo':   marcacion.tipo,
                'estado': marcacion.estado,
                'fecha':  marcacion.fecha,
            },
            'ubicacion': {
                'ip':     ip,
                'ciudad': ciudad,
                'pais':   pais,
            }
        }, status=status.HTTP_200_OK)