# reconocimiento/views.py — con validación IP + geocerca + geolocalización

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from apps.trabajadores.models import Trabajador
from apps.marcaciones.services import registrar_marcacion
from apps.marcaciones.ip_service import get_client_ip, validar_ip_autorizada, obtener_info_ip
from apps.marcaciones.geo_service import validar_geocerca          # ← NUEVO
from apps.configuracion.models import ConfiguracionSistema
from apps.usuarios.models import Usuario
from apps.auditoria.services import registrar_auditoria
from .services import generar_embedding, generar_embedding_promedio, comparar_embeddings
from apps.usuarios.permissions import EsAdmin
import numpy as np
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
        try:
            trabajador_id = request.data.get('trabajador_id')
            imagen_base64 = request.data.get('imagen')
            dispositivo   = request.data.get('dispositivo', 'No especificado')
            latitud       = request.data.get('latitud')
            longitud      = request.data.get('longitud')
            navegador     = request.data.get('navegador', '')   # ← NUEVO

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

            # ── IP ──────────────────────────────────────────────────────
            ip = get_client_ip(request)
            print("IP detectada:", ip)

            ip_ok, ip_error = validar_ip_autorizada(ip, config)
            if not ip_ok:
                registrar_auditoria(
                    usuario=usuario,
                    accion='ACCESO_IP_DENEGADO',
                    descripcion=f'Intento desde IP no autorizada: {ip}',
                    ip=ip
                )
                return Response({'error': ip_error}, status=status.HTTP_403_FORBIDDEN)

            # ── DIAGNÓSTICO DEL EMBEDDING EN BD ────────────────────────
            emb_bd = trabajador.embedding
            if emb_bd:
                arr_bd = np.array(emb_bd, dtype=np.float64)
                print(f"[Diagnóstico BD] dim={arr_bd.shape[0]} | norma={np.linalg.norm(arr_bd):.6f}")

            # ── RECONOCIMIENTO FACIAL ───────────────────────────────────
            print("Generando embedding...")
            embedding_capturado, error = generar_embedding(imagen_base64)

            if error:
                print("Error embedding:", error)
                return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

            print("Comparando embeddings...")
            verificado, similitud = comparar_embeddings(
                embedding_capturado,
                trabajador.embedding,
                config.umbral_similitud
            )

            # ── FALLÓ EL ROSTRO ─────────────────────────────────────────
            if not verificado:
                usuario.intentos_fallidos += 1

                if usuario.intentos_fallidos >= config.max_intentos_faciales:
                    usuario.bloqueado = True
                    usuario.save()
                    registrar_auditoria(
                        usuario=usuario,
                        accion='VERIFICACION_FALLIDA',
                        descripcion=f'Bloqueado. Similitud: {similitud:.2f}. IP: {ip}',
                        ip=ip
                    )
                    return Response(
                        {'error': 'Usuario bloqueado por intentos faciales fallidos'},
                        status=status.HTTP_403_FORBIDDEN
                    )

                usuario.save()
                restantes = config.max_intentos_faciales - usuario.intentos_fallidos
                registrar_auditoria(
                    usuario=usuario,
                    accion='VERIFICACION_FALLIDA',
                    descripcion=f'No coincide. Similitud: {similitud:.2f}. Intentos: {usuario.intentos_fallidos}',
                    ip=ip
                )
                return Response({
                    'error': f'El rostro no coincide. Intentos restantes: {restantes}',
                    'similitud':          round(similitud, 2),
                    'intentos_restantes': restantes
                }, status=status.HTTP_401_UNAUTHORIZED)

            # ── ÉXITO FACIAL ────────────────────────────────────────────
            usuario.intentos_fallidos = 0
            usuario.save()
            print("Verificación facial exitosa")

            # ══════════════════════════════════════════════════════════════
            # VALIDACIÓN DE GEOCERCA
            # Se ejecuta DESPUÉS del reconocimiento facial (no gastamos
            # recursos en geocerca si el rostro ya no coincide) y ANTES
            # de registrar_marcacion() para que el rechazo no cree registro.
            # ══════════════════════════════════════════════════════════════
            permitido, mensaje_rechazo, auditoria_data = validar_geocerca(
                latitud=latitud,
                longitud=longitud,
                config=config,
                ip=ip,
                dispositivo=dispositivo,
                navegador=navegador,
            )

            if not permitido:
                if config.geocerca_auditoria and auditoria_data:
                    try:
                        registrar_auditoria(
                            usuario=usuario,
                            accion='GEOCERCA_RECHAZO',
                            descripcion=(
                                f'Trabajador ID={trabajador_id} | '
                                f'Motivo: {auditoria_data.get("motivo")} | '
                                f'Lat: {auditoria_data.get("latitud_reportada")} | '
                                f'Lon: {auditoria_data.get("longitud_reportada")} | '
                                f'Distancia: {auditoria_data.get("distancia_metros")}m | '
                                f'IP: {ip} | Dispositivo: {dispositivo}'
                            ),
                            ip=ip,
                        )
                    except Exception:
                        pass

                return Response(
                    {
                        'error':  mensaje_rechazo,
                        'codigo': 'GEOCERCA_RECHAZADO',
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            # ── GEOCERCA OK → registrar marcación ───────────────────────
            info_ip     = obtener_info_ip(ip)
            ciudad      = info_ip.get('ciudad', '')
            pais        = info_ip.get('pais', '')
            ip_info_str = f"{info_ip.get('org', '')} / {info_ip.get('isp', '')}".strip(' /')

            print("Registrando marcación...")
            marcacion, mensaje = registrar_marcacion(
                trabajador, ip, dispositivo,
                latitud=latitud,
                longitud=longitud,
                ciudad=ciudad,
                pais=pais,
                ip_info=ip_info_str or None,
            )

            if marcacion is None:
                print("Error marcación:", mensaje)
                return Response({'error': mensaje}, status=status.HTTP_400_BAD_REQUEST)

            # Auditoría geocerca aprobada
            if config.geocerca_activa and config.geocerca_auditoria and auditoria_data:
                try:
                    registrar_auditoria(
                        usuario=usuario,
                        accion='GEOCERCA_APROBADO',
                        descripcion=(
                            f'Trabajador ID={trabajador_id} | '
                            f'Distancia: {auditoria_data.get("distancia_metros")}m | '
                            f'IP: {ip} | Dispositivo: {dispositivo}'
                        ),
                        ip=ip,
                    )
                except Exception:
                    pass

            registrar_auditoria(
                usuario=usuario,
                accion='MARCACION_EXITOSA',
                descripcion=f'Marcación {marcacion.tipo} - {ciudad}, {pais}',
                ip=ip
            )

            return Response({
                'mensaje':   mensaje,
                'similitud': similitud,
                'marcacion': {
                    'id':              marcacion.id,
                    'tipo':            marcacion.tipo,
                    'estado':          marcacion.estado,
                    'fecha':           marcacion.fecha,
                    'va_a_asistencia': marcacion.va_a_asistencia,
                },
                'ubicacion': {
                    'ip':     ip,
                    'ciudad': ciudad,
                    'pais':   pais,
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print("\nERROR 500 EN VERIFICAR ROSTRO")
            traceback.print_exc()
            return Response(
                {'error': 'Error interno del servidor', 'detalle': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )