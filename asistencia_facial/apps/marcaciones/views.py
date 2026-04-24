from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Marcacion
from .serializers import MarcacionSerializer
from .services import registrar_marcacion
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from zoneinfo import ZoneInfo
from datetime import datetime, date, timedelta
from django.utils import timezone
from apps.trabajadores.models import Trabajador
from apps.usuarios.permissions import EsAdmin
from rest_framework.permissions import IsAuthenticated
from apps.configuracion.models import ConfiguracionSistema


class MarcacionRegistrarView(APIView):

    def post(self, request):
        trabajador_id = request.data.get('trabajador_id')
        dispositivo   = request.data.get('dispositivo', 'No especificado')
        latitud       = request.data.get('latitud')
        longitud      = request.data.get('longitud')
        ciudad        = request.data.get('ciudad')
        pais          = request.data.get('pais')
        ip_info       = request.data.get('ip_info')

        if not trabajador_id:
            return Response(
                {'error': 'El trabajador_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            trabajador = Trabajador.objects.get(pk=trabajador_id)
        except Trabajador.DoesNotExist:
            return Response(
                {'error': 'Trabajador no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not trabajador.activo:
            return Response(
                {'error': 'Trabajador inactivo'},
                status=status.HTTP_403_FORBIDDEN
            )

        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')

        marcacion, mensaje = registrar_marcacion(
            trabajador, ip, dispositivo,
            latitud, longitud, ciudad, pais, ip_info
        )

        if marcacion is None:
            return Response(
                {'error': mensaje},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = MarcacionSerializer(marcacion)
        return Response(
            {**serializer.data, 'mensaje': mensaje},
            status=status.HTTP_201_CREATED
        )


class MarcacionHistorialView(APIView):
    """Historial COMPLETO: todas las marcaciones sin filtro de va_a_asistencia."""

    def get(self, request, trabajador_id):
        try:
            trabajador = Trabajador.objects.get(pk=trabajador_id)
        except Trabajador.DoesNotExist:
            return Response(
                {'error': 'Trabajador no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        marcaciones = Marcacion.objects.filter(
            trabajador=trabajador
        ).order_by('-fecha')

        serializer = MarcacionSerializer(marcaciones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MarcacionListarView(APIView):
    permission_classes = [EsAdmin]

    def get(self, request):
        marcaciones = Marcacion.objects.all().order_by('-fecha')
        serializer = MarcacionSerializer(marcaciones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MarcacionHoyView(APIView):
    permission_classes = [EsAdmin]

    def get(self, request):
        ahora_local = timezone.localtime(timezone.now())
        inicio_dia  = ahora_local.replace(hour=0,  minute=0,  second=0,  microsecond=0)
        fin_dia     = ahora_local.replace(hour=23, minute=59, second=59, microsecond=999999)

        marcaciones = Marcacion.objects.filter(
            fecha__gte=inicio_dia,
            fecha__lte=fin_dia,
            exitoso=True,
            va_a_asistencia=True,
        ).order_by('fecha').select_related('trabajador')

        data = []
        for m in marcaciones:
            fecha_local  = timezone.localtime(m.fecha)
            tipo_display = 'ENTRADA' if m.tipo in ('ENTRADA_VALIDA', 'ENTRADA') else 'SALIDA'
            data.append({
                'id':                m.id,
                'trabajador_id':     m.trabajador.id,
                'trabajador_nombre': f'{m.trabajador.nombres} {m.trabajador.apellido_paterno} {m.trabajador.apellido_materno}',
                'dni':               m.trabajador.dni,
                'cargo':             m.trabajador.cargo,
                'tipo':              tipo_display,
                'estado':            m.estado,
                'fecha':             fecha_local.strftime('%Y-%m-%dT%H:%M:%S%z'),
                'dispositivo':       m.dispositivo,
                'latitud':           str(m.latitud)  if m.latitud  else None,
                'longitud':          str(m.longitud) if m.longitud else None,
            })

        return Response({
            'fecha':       ahora_local.date(),
            'total':       len(data),
            'marcaciones': data
        }, status=status.HTTP_200_OK)


class ReporteRangoFechasView(APIView):
    permission_classes = [EsAdmin]

    def get(self, request):
        fecha_inicio      = request.query_params.get('fecha_inicio')
        fecha_fin         = request.query_params.get('fecha_fin')
        trabajador_id     = request.query_params.get('trabajador_id')
        estado_trabajador = request.query_params.get('estado_trabajador')  # 'activos' | 'inactivos'

        if not fecha_inicio or not fecha_fin:
            return Response(
                {'error': 'fecha_inicio y fecha_fin son requeridos. Formato: YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fin    = datetime.strptime(fecha_fin,    '%Y-%m-%d')
            fin    = fin.replace(hour=23, minute=59, second=59)
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        lima_tz = ZoneInfo('America/Lima')
        inicio  = inicio.replace(tzinfo=lima_tz)
        fin     = fin.replace(tzinfo=lima_tz)

        marcaciones = Marcacion.objects.filter(
            fecha__gte=inicio,
            fecha__lte=fin,
            exitoso=True,
            va_a_asistencia=True,
        ).order_by('-fecha').select_related('trabajador')

        # Filtro por trabajador específico o por estado
        if trabajador_id:
            marcaciones = marcaciones.filter(trabajador_id=trabajador_id)
        elif estado_trabajador == 'activos':
            marcaciones = marcaciones.filter(trabajador__activo=True)
        elif estado_trabajador == 'inactivos':
            marcaciones = marcaciones.filter(trabajador__activo=False)

        total_entradas  = marcaciones.filter(tipo__in=['ENTRADA_VALIDA', 'ENTRADA']).count()
        total_puntuales = marcaciones.filter(tipo__in=['ENTRADA_VALIDA', 'ENTRADA'], estado='PUNTUAL').count()
        total_tardanzas = marcaciones.filter(tipo__in=['ENTRADA_VALIDA', 'ENTRADA'], estado='TARDANZA').count()

        data = []
        for m in marcaciones:
            fecha_local  = timezone.localtime(m.fecha)
            tipo_display = 'ENTRADA' if m.tipo in ('ENTRADA_VALIDA', 'ENTRADA') else 'SALIDA'
            data.append({
                'id':                m.id,
                'trabajador_id':     m.trabajador.id,
                'trabajador_nombre': f'{m.trabajador.nombres} {m.trabajador.apellido_paterno} {m.trabajador.apellido_materno}',
                'dni':               m.trabajador.dni,
                'cargo':             m.trabajador.cargo,
                'tipo':              tipo_display,
                'estado':            m.estado,
                'fecha':             fecha_local.strftime('%Y-%m-%dT%H:%M:%S%z'),
                'dispositivo':       m.dispositivo,
            })

        return Response({
            'fecha_inicio':    fecha_inicio,
            'fecha_fin':       fecha_fin,
            'total_registros': len(data),
            'estadisticas': {
                'total_entradas': total_entradas,
                'puntuales':      total_puntuales,
                'tardanzas':      total_tardanzas,
            },
            'marcaciones': data
        }, status=status.HTTP_200_OK)


class ReportePDFView(APIView):
    permission_classes = [EsAdmin]

    def get(self, request):
        fecha_inicio      = request.query_params.get('fecha_inicio')
        fecha_fin         = request.query_params.get('fecha_fin')
        trabajador_id     = request.query_params.get('trabajador_id')
        estado_trabajador = request.query_params.get('estado_trabajador')  # 'activos' | 'inactivos'

        if not fecha_inicio or not fecha_fin:
            return Response(
                {'error': 'fecha_inicio y fecha_fin son requeridos. Formato: YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lima_tz = ZoneInfo('America/Lima')
            inicio  = datetime.strptime(fecha_inicio, '%Y-%m-%d').replace(hour=0,  minute=0,  second=0,  tzinfo=lima_tz)
            fin     = datetime.strptime(fecha_fin,    '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=lima_tz)
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.utils import timezone as tz
        marcaciones = Marcacion.objects.filter(
            fecha__gte=inicio,
            fecha__lte=fin,
            exitoso=True,
            va_a_asistencia=True,
        ).order_by('-fecha').select_related('trabajador')

        # Filtro por trabajador específico o por estado
        if trabajador_id:
            marcaciones = marcaciones.filter(trabajador_id=trabajador_id)
        elif estado_trabajador == 'activos':
            marcaciones = marcaciones.filter(trabajador__activo=True)
        elif estado_trabajador == 'inactivos':
            marcaciones = marcaciones.filter(trabajador__activo=False)

        total_entradas  = marcaciones.filter(tipo__in=['ENTRADA_VALIDA', 'ENTRADA']).count()
        total_puntuales = marcaciones.filter(tipo__in=['ENTRADA_VALIDA', 'ENTRADA'], estado='PUNTUAL').count()
        total_tardanzas = marcaciones.filter(tipo__in=['ENTRADA_VALIDA', 'ENTRADA'], estado='TARDANZA').count()

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=1.5*cm, leftMargin=1.5*cm,
            topMargin=1.5*cm,   bottomMargin=1.5*cm
        )

        styles = getSampleStyleSheet()
        story  = []

        estilo_titulo = ParagraphStyle(
            'titulo', parent=styles['Normal'],
            fontSize=14, fontName='Helvetica-Bold',
            alignment=TA_CENTER, spaceAfter=4,
            textColor=colors.HexColor('#1a3a6b'),
        )
        estilo_subtitulo = ParagraphStyle(
            'subtitulo', parent=styles['Normal'],
            fontSize=10, fontName='Helvetica',
            alignment=TA_CENTER, spaceAfter=2,
            textColor=colors.HexColor('#333333'),
        )
        estilo_seccion = ParagraphStyle(
            'seccion', parent=styles['Normal'],
            fontSize=10, fontName='Helvetica-Bold',
            spaceAfter=6, spaceBefore=10,
            textColor=colors.HexColor('#1a3a6b'),
        )

        story.append(Paragraph('MUNICIPALIDAD PROVINCIAL DE CAJAMARCA', estilo_titulo))
        story.append(Paragraph('Sistema de Control de Asistencia', estilo_subtitulo))
        story.append(Paragraph('REPORTE DE ASISTENCIA', estilo_subtitulo))
        story.append(HRFlowable(width='100%', thickness=2, color=colors.HexColor('#1a3a6b')))
        story.append(Spacer(1, 0.3*cm))

        fecha_generacion = tz.localtime(tz.now()).strftime('%d/%m/%Y %H:%M')

        # Etiqueta del filtro aplicado para el PDF
        if trabajador_id:
            filtro_label = None  # se agrega abajo con el nombre del trabajador
        elif estado_trabajador == 'activos':
            filtro_label = 'Solo trabajadores activos'
        elif estado_trabajador == 'inactivos':
            filtro_label = 'Solo trabajadores inactivos'
        else:
            filtro_label = 'Todos los trabajadores'

        info_data = [
            ['Período:',      f'{fecha_inicio} al {fecha_fin}'],
            ['Filtro:',       filtro_label or 'Trabajador específico'],
            ['Generado:',     fecha_generacion],
            ['Generado por:', f'{request.user.trabajador.nombres} {request.user.trabajador.apellido_paterno}'],
        ]
        if trabajador_id:
            try:
                t = Trabajador.objects.get(pk=trabajador_id)
                info_data.append(['Trabajador:', f'{t.nombres} {t.apellido_paterno} {t.apellido_materno}'])
            except Exception:
                pass

        tabla_info = Table(info_data, colWidths=[3.5*cm, 12*cm])
        tabla_info.setStyle(TableStyle([
            ('FONTNAME',      (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME',      (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE',      (0, 0), (-1, -1), 9),
            ('TEXTCOLOR',     (0, 0), (0, -1), colors.HexColor('#1a3a6b')),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(tabla_info)
        story.append(Spacer(1, 0.4*cm))

        story.append(Paragraph('RESUMEN', estilo_seccion))
        stats_data = [
            ['Total registros', 'Total entradas', 'Puntuales', 'Tardanzas'],
            [str(marcaciones.count()), str(total_entradas), str(total_puntuales), str(total_tardanzas)],
        ]
        tabla_stats = Table(stats_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
        tabla_stats.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0), colors.HexColor('#1a3a6b')),
            ('TEXTCOLOR',     (0, 0), (-1, 0), colors.white),
            ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE',      (0, 0), (-1, -1), 9),
            ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.HexColor('#eaf0fb'), colors.white]),
            ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('TOPPADDING',    (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(tabla_stats)
        story.append(Spacer(1, 0.4*cm))

        story.append(Paragraph('DETALLE DE MARCACIONES', estilo_seccion))
        headers    = ['#', 'Trabajador', 'DNI', 'Tipo', 'Estado', 'Fecha y Hora', 'Dispositivo']
        tabla_data = [headers]

        for i, m in enumerate(marcaciones, 1):
            fecha_local  = tz.localtime(m.fecha).strftime('%d/%m/%Y %H:%M')
            tipo_display = 'ENTRADA' if m.tipo in ('ENTRADA_VALIDA', 'ENTRADA') else 'SALIDA'
            estado       = m.estado if m.estado else '-'
            tabla_data.append([
                str(i),
                f'{m.trabajador.nombres} {m.trabajador.apellido_paterno}',
                m.trabajador.dni,
                tipo_display,
                estado,
                fecha_local,
                m.dispositivo,
            ])

        tabla = Table(
            tabla_data,
            colWidths=[0.8*cm, 5*cm, 2*cm, 1.8*cm, 2*cm, 3.5*cm, 2.4*cm]
        )
        tabla.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0), colors.HexColor('#1a3a6b')),
            ('TEXTCOLOR',     (0, 0), (-1, 0), colors.white),
            ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME',      (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE',      (0, 0), (-1, -1), 7.5),
            ('ALIGN',         (0, 0), (0, -1), 'CENTER'),
            ('ALIGN',         (2, 0), (5, -1), 'CENTER'),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.HexColor('#eaf0fb'), colors.white]),
            ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('TOPPADDING',    (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(tabla)
        story.append(Spacer(1, 0.5*cm))
        story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#1a3a6b')))
        story.append(Spacer(1, 0.2*cm))
        estilo_pie = ParagraphStyle('pie', parent=styles['Normal'], fontSize=7, alignment=TA_CENTER, textColor=colors.grey)
        story.append(Paragraph('Municipalidad Provincial de Cajamarca — Sistema de Control de Asistencia', estilo_pie))
        story.append(Paragraph(f'Documento generado el {fecha_generacion}', estilo_pie))

        doc.build(story)
        buffer.seek(0)

        nombre_archivo = f'reporte_asistencia_{fecha_inicio}_{fecha_fin}.pdf'
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        return response


class EstadisticasDashboardView(APIView):
    permission_classes = [EsAdmin]

    def get(self, request):
        MESES = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo',  6: 'Junio',   7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }

        ahora_local = timezone.localtime(timezone.now())
        inicio_hoy  = ahora_local.replace(hour=0,  minute=0,  second=0,  microsecond=0)
        fin_hoy     = ahora_local.replace(hour=23, minute=59, second=59, microsecond=999999)
        inicio_mes  = ahora_local.replace(day=1,   hour=0,    minute=0,  second=0, microsecond=0)

        total_trabajadores  = Trabajador.objects.filter(activo=True).count()
        total_con_embedding = Trabajador.objects.filter(activo=True, embedding__isnull=False).count()

        marcaciones_hoy = Marcacion.objects.filter(
            fecha__gte=inicio_hoy,
            fecha__lte=fin_hoy,
            exitoso=True,
            va_a_asistencia=True,
        )
        entradas_hoy  = marcaciones_hoy.filter(tipo__in=['ENTRADA_VALIDA', 'ENTRADA']).count()
        puntuales_hoy = marcaciones_hoy.filter(tipo__in=['ENTRADA_VALIDA', 'ENTRADA'], estado='PUNTUAL').count()
        tardanzas_hoy = marcaciones_hoy.filter(tipo__in=['ENTRADA_VALIDA', 'ENTRADA'], estado='TARDANZA').count()
        salidas_hoy   = marcaciones_hoy.filter(tipo__in=['SALIDA_VALIDA',  'SALIDA']).count()

        marcaciones_mes = Marcacion.objects.filter(
            fecha__gte=inicio_mes,
            exitoso=True,
            va_a_asistencia=True,
        )
        entradas_mes  = marcaciones_mes.filter(tipo__in=['ENTRADA_VALIDA', 'ENTRADA']).count()
        puntuales_mes = marcaciones_mes.filter(tipo__in=['ENTRADA_VALIDA', 'ENTRADA'], estado='PUNTUAL').count()
        tardanzas_mes = marcaciones_mes.filter(tipo__in=['ENTRADA_VALIDA', 'ENTRADA'], estado='TARDANZA').count()

        porcentaje_puntualidad = 0
        if entradas_mes > 0:
            porcentaje_puntualidad = round((puntuales_mes / entradas_mes) * 100, 1)

        return Response({
            'fecha_actual': ahora_local.strftime('%d/%m/%Y %H:%M'),
            'trabajadores': {
                'total_activos':  total_trabajadores,
                'con_embedding':  total_con_embedding,
                'sin_embedding':  total_trabajadores - total_con_embedding,
            },
            'hoy': {
                'entradas':   entradas_hoy,
                'salidas':    salidas_hoy,
                'puntuales':  puntuales_hoy,
                'tardanzas':  tardanzas_hoy,
                'sin_marcar': total_trabajadores - entradas_hoy,
            },
            'mes_actual': {
                'mes':                    f"{MESES[ahora_local.month]} {ahora_local.year}",
                'total_entradas':         entradas_mes,
                'puntuales':              puntuales_mes,
                'tardanzas':              tardanzas_mes,
                'porcentaje_puntualidad': porcentaje_puntualidad,
            }
        }, status=status.HTTP_200_OK)


DIAS_SEMANA = {
    0: 'Lunes', 1: 'Martes', 2: 'Miércoles',
    3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
}

MESES_ES = {
    1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
    5: 'mayo',  6: 'junio',   7: 'julio', 8: 'agosto',
    9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
}


def calcular_tiempo_trabajado(entrada_dt, salida_dt):
    if not entrada_dt or not salida_dt:
        return None
    delta          = salida_dt - entrada_dt
    total_segundos = int(delta.total_seconds())
    if total_segundos < 0:
        return None
    horas    = total_segundos // 3600
    minutos  = (total_segundos % 3600) // 60
    segundos = total_segundos % 60
    return f'{horas:02d}:{minutos:02d}:{segundos:02d}'


def agrupar_marcaciones_por_dia(marcaciones_qs, fecha_inicio_date=None, fecha_fin_date=None, hoy=None):
    config          = ConfiguracionSistema.objects.first()
    hora_fin_salida = config.hora_fin_salida if config else None

    ahora_local = timezone.localtime(timezone.now())
    hoy_real    = ahora_local.date()
    hora_ahora  = ahora_local.time()

    dias = {}

    for m in marcaciones_qs:
        if not m.va_a_asistencia:
            continue

        fecha_local = timezone.localtime(m.fecha)
        dia_key     = fecha_local.date().isoformat()

        if dia_key not in dias:
            dias[dia_key] = {
                'fecha':          dia_key,
                'dia_semana':     DIAS_SEMANA[fecha_local.weekday()],
                'dia_texto':      f"{DIAS_SEMANA[fecha_local.weekday()]} {fecha_local.day} de {MESES_ES[fecha_local.month]}",
                'entrada':        None,
                'entrada_hora':   None,
                'entrada_estado': None,
                'salida':         None,
                'salida_hora':    None,
                'tiempo_trabajado': None,
                'resultado':      'FALTA',
            }

        if m.tipo in ('ENTRADA_VALIDA', 'ENTRADA') and not dias[dia_key]['entrada']:
            dias[dia_key]['entrada']        = fecha_local.isoformat()
            dias[dia_key]['entrada_hora']   = fecha_local.strftime('%I:%M:%S %p')
            dias[dia_key]['entrada_estado'] = m.estado

        if m.tipo in ('SALIDA_VALIDA', 'SALIDA') and not dias[dia_key]['salida']:
            dias[dia_key]['salida']      = fecha_local.isoformat()
            dias[dia_key]['salida_hora'] = fecha_local.strftime('%I:%M:%S %p')

    for dia_key, dia in dias.items():
        entrada_dt = datetime.fromisoformat(dia['entrada']) if dia['entrada'] else None
        salida_dt  = datetime.fromisoformat(dia['salida'])  if dia['salida']  else None

        dia['tiempo_trabajado'] = calcular_tiempo_trabajado(entrada_dt, salida_dt)

        fecha_dia = date.fromisoformat(dia_key)

        if fecha_dia.weekday() >= 5:
            dia['resultado'] = 'NO_LABORABLE'
            continue

        if dia['entrada'] and dia['salida']:
            dia['resultado'] = 'TARDANZA' if dia['entrada_estado'] == 'TARDANZA' else 'ASISTIÓ'
        elif dia['entrada'] and not dia['salida']:
            if fecha_dia == hoy_real and hora_fin_salida and hora_ahora <= hora_fin_salida:
                dia['resultado'] = 'PENDIENTE'
            else:
                dia['resultado'] = 'INCOMPLETO'
        else:
            if fecha_dia == hoy_real and hora_fin_salida and hora_ahora <= hora_fin_salida:
                dia['resultado'] = 'PENDIENTE'
            else:
                dia['resultado'] = 'FALTA'

    if fecha_inicio_date and fecha_fin_date:
        dia_actual = fecha_inicio_date
        while dia_actual <= fecha_fin_date:
            iso = dia_actual.isoformat()
            if iso not in dias:
                if dia_actual.weekday() >= 5:
                    dia_actual += timedelta(days=1)
                    continue
                if hoy is None or dia_actual <= hoy:
                    if dia_actual == hoy_real and hora_fin_salida and hora_ahora <= hora_fin_salida:
                        resultado = 'PENDIENTE'
                    else:
                        resultado = 'FALTA'
                    dias[iso] = {
                        'fecha':          iso,
                        'dia_semana':     DIAS_SEMANA[dia_actual.weekday()],
                        'dia_texto':      f"{DIAS_SEMANA[dia_actual.weekday()]} {dia_actual.day} de {MESES_ES[dia_actual.month]}",
                        'entrada':        None,
                        'entrada_hora':   None,
                        'entrada_estado': None,
                        'salida':         None,
                        'salida_hora':    None,
                        'tiempo_trabajado': None,
                        'resultado':      resultado,
                    }
            dia_actual += timedelta(days=1)

    return sorted(dias.values(), key=lambda x: x['fecha'], reverse=True)


class AsistenciaResumenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        trabajador_id = request.user.trabajador.id
        ahora_local   = timezone.localtime(timezone.now())
        lima_tz       = ZoneInfo('America/Lima')

        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin    = request.query_params.get('fecha_fin')

        if fecha_inicio and fecha_fin:
            try:
                inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').replace(hour=0,  minute=0,  second=0,  tzinfo=lima_tz)
                fin    = datetime.strptime(fecha_fin,    '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=lima_tz)
            except ValueError:
                return Response({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            inicio = ahora_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            fin    = ahora_local.replace(hour=23, minute=59, second=59, microsecond=999999)

        marcaciones = Marcacion.objects.filter(
            trabajador_id=trabajador_id,
            fecha__gte=inicio,
            fecha__lte=fin,
            exitoso=True,
        ).order_by('fecha')

        dias = agrupar_marcaciones_por_dia(
            marcaciones,
            fecha_inicio_date=inicio.date(),
            fecha_fin_date=fin.date(),
            hoy=ahora_local.date()
        )

        dias_laborables = [d for d in dias if d['resultado'] != 'NO_LABORABLE']
        total_dias      = len(dias_laborables)
        asistencias     = sum(1 for d in dias_laborables if d['resultado'] in ('ASISTIÓ', 'TARDANZA'))
        tardanzas       = sum(1 for d in dias_laborables if d['resultado'] == 'TARDANZA')
        faltas          = sum(1 for d in dias_laborables if d['resultado'] == 'FALTA')

        return Response({
            'periodo': {
                'inicio': fecha_inicio or inicio.date().isoformat(),
                'fin':    fecha_fin    or fin.date().isoformat(),
            },
            'resumen': {
                'total_dias':  total_dias,
                'asistencias': asistencias,
                'tardanzas':   tardanzas,
                'faltas':      faltas,
            },
            'dias': dias
        }, status=status.HTTP_200_OK)


class AsistenciaAdminView(APIView):
    permission_classes = [EsAdmin]

    def get(self, request):
        trabajador_id = request.query_params.get('trabajador_id')
        if not trabajador_id:
            return Response({'error': 'trabajador_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            trabajador = Trabajador.objects.get(pk=trabajador_id)
        except Trabajador.DoesNotExist:
            return Response({'error': 'Trabajador no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        lima_tz     = ZoneInfo('America/Lima')
        ahora_local = timezone.localtime(timezone.now())

        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin    = request.query_params.get('fecha_fin')

        if fecha_inicio and fecha_fin:
            try:
                inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').replace(hour=0,  minute=0,  second=0,  tzinfo=lima_tz)
                fin    = datetime.strptime(fecha_fin,    '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=lima_tz)
            except ValueError:
                return Response({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            inicio = ahora_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            fin    = ahora_local.replace(hour=23, minute=59, second=59, microsecond=999999)

        marcaciones = Marcacion.objects.filter(
            trabajador_id=trabajador_id,
            fecha__gte=inicio,
            fecha__lte=fin,
            exitoso=True,
        ).order_by('fecha')

        dias = agrupar_marcaciones_por_dia(
            marcaciones,
            fecha_inicio_date=inicio.date(),
            fecha_fin_date=fin.date(),
            hoy=ahora_local.date()
        )

        dias_laborables = [d for d in dias if d['resultado'] != 'NO_LABORABLE']
        total_dias      = len(dias_laborables)
        asistencias     = sum(1 for d in dias_laborables if d['resultado'] in ('ASISTIÓ', 'TARDANZA'))
        tardanzas       = sum(1 for d in dias_laborables if d['resultado'] == 'TARDANZA')
        faltas          = sum(1 for d in dias_laborables if d['resultado'] == 'FALTA')

        return Response({
            'trabajador': {
                'id':     trabajador.id,
                'nombre': f'{trabajador.nombres} {trabajador.apellido_paterno} {trabajador.apellido_materno}',
                'dni':    trabajador.dni,
                'cargo':  trabajador.cargo,
            },
            'periodo': {
                'inicio': fecha_inicio or inicio.date().isoformat(),
                'fin':    fecha_fin    or fin.date().isoformat(),
            },
            'resumen': {
                'total_dias':  total_dias,
                'asistencias': asistencias,
                'tardanzas':   tardanzas,
                'faltas':      faltas,
            },
            'dias': dias
        }, status=status.HTTP_200_OK)


class EditarMarcacionAdminView(APIView):
    permission_classes = [EsAdmin]

    def patch(self, request):
        trabajador_id = request.data.get('trabajador_id')
        fecha_str     = request.data.get('fecha')
        entrada_hora  = request.data.get('entrada_hora')
        salida_hora   = request.data.get('salida_hora')

        if not all([trabajador_id, fecha_str, entrada_hora]):
            return Response({'error': 'Faltan datos'}, status=400)

        try:
            trabajador = Trabajador.objects.get(pk=trabajador_id)
            fecha      = date.fromisoformat(fecha_str)
        except (Trabajador.DoesNotExist, ValueError):
            return Response({'error': 'Datos inválidos'}, status=400)

        lima_tz    = ZoneInfo('America/Lima')
        inicio_dia = datetime(fecha.year, fecha.month, fecha.day, 0,  0,  0,  tzinfo=lima_tz)
        fin_dia    = datetime(fecha.year, fecha.month, fecha.day, 23, 59, 59, tzinfo=lima_tz)

        def construir_datetime(hora_str):
            from datetime import time as dtime
            h, m = map(int, hora_str.split(':'))
            return datetime.combine(fecha, dtime(h, m)).replace(tzinfo=lima_tz)

        entradas = list(Marcacion.objects.filter(
            trabajador=trabajador,
            fecha__gte=inicio_dia,
            fecha__lte=fin_dia,
            tipo__in=['ENTRADA_VALIDA', 'ENTRADA'],
        ).order_by('fecha'))

        nueva_entrada_dt = construir_datetime(entrada_hora)

        if entradas:
            primera = entradas[0]
            primera.fecha           = nueva_entrada_dt
            primera.va_a_asistencia = True
            primera.save(update_fields=['fecha', 'va_a_asistencia'])
            if len(entradas) > 1:
                Marcacion.objects.filter(id__in=[e.id for e in entradas[1:]]).delete()
        else:
            Marcacion.objects.create(
                trabajador=trabajador, fecha=nueva_entrada_dt,
                tipo='ENTRADA_VALIDA', estado='PUNTUAL',
                exitoso=True, va_a_asistencia=True,
            )

        salidas = list(Marcacion.objects.filter(
            trabajador=trabajador,
            fecha__gte=inicio_dia,
            fecha__lte=fin_dia,
            tipo__in=['SALIDA_VALIDA', 'SALIDA'],
        ).order_by('fecha'))

        if salida_hora:
            nueva_salida_dt = construir_datetime(salida_hora)
            if salidas:
                primera_salida = salidas[0]
                primera_salida.fecha           = nueva_salida_dt
                primera_salida.va_a_asistencia = True
                primera_salida.save(update_fields=['fecha', 'va_a_asistencia'])
                if len(salidas) > 1:
                    Marcacion.objects.filter(id__in=[s.id for s in salidas[1:]]).delete()
            else:
                Marcacion.objects.create(
                    trabajador=trabajador, fecha=nueva_salida_dt,
                    tipo='SALIDA_VALIDA', exitoso=True, va_a_asistencia=True,
                )
        else:
            Marcacion.objects.filter(
                trabajador=trabajador,
                fecha__gte=inicio_dia,
                fecha__lte=fin_dia,
                tipo__in=['SALIDA_VALIDA', 'SALIDA'],
            ).delete()

        return Response({'ok': True})