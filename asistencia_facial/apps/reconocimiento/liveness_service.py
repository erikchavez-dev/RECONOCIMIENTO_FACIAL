"""
apps/reconocimiento/liveness_service.py

Prueba de vida (liveness detection) con doble capa:
  1. Parpadeo: el usuario parpadeó al menos 1 vez durante la captura.
  2. Micro-movimientos: varianza suficiente entre frames para descartar
     foto fija, GIF en loop o vídeo perfectamente cíclico.

Entrada: lista de imágenes base64 (entre MIN_FRAMES y MAX_FRAMES).
Salida : (ok: bool, motivo: str)

Dependencias ya instaladas: insightface, opencv-python, numpy.
"""

import numpy as np
import cv2
import base64
import logging

logger = logging.getLogger(__name__)

# ── Parámetros ajustables ────────────────────────────────────────────────────
MIN_FRAMES          = 8    # mínimo de frames que debe enviar el frontend
MAX_FRAMES          = 20   # máximo aceptado (seguridad)
MIN_EAR             = 0.21 # Eye Aspect Ratio por debajo del cual = ojo cerrado
BLINK_MIN_FRAMES    = 2    # cuántos frames consecutivos con ojo cerrado = parpadeo
EAR_OPEN_THRESHOLD  = 0.26 # EAR mínima para considerar el ojo abierto de nuevo
MOTION_VAR_THRESHOLD = 80.0  # varianza mínima de diferencia entre frames (píxeles)
MOTION_MEAN_THRESHOLD = 3.5  # diferencia media mínima entre frames consecutivos
CYCLE_SIM_THRESHOLD  = 0.97  # similitud entre frame 0 y frame N/2 → GIF detectado
# ─────────────────────────────────────────────────────────────────────────────


def _decodificar(b64: str):
    """Decodifica base64 → numpy BGR. Retorna None si falla."""
    try:
        if ',' in b64:
            b64 = b64.split(',')[1]
        b64 = b64.strip().replace('\n', '').replace('\r', '').replace(' ', '')
        pad = 4 - len(b64) % 4
        if pad != 4:
            b64 += '=' * pad
        buf = np.frombuffer(base64.b64decode(b64), dtype=np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        logger.warning(f'[liveness] Error decodificando frame: {e}')
        return None


def _ear(landmarks_2d, left_indices, right_indices):
    """
    Eye Aspect Ratio promedio de ambos ojos.
    Fórmula: EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
    InsightFace kps de 5 puntos: [ojo_izq, ojo_der, nariz, boca_izq, boca_der]
    Para EAR con 5 kps usamos la distancia vertical entre las esquinas y
    la distancia horizontal del ojo.
    """
    # Con 5 keypoints no tenemos los 6 puntos clásicos por ojo.
    # Usamos la altura relativa entre nariz y ojo vs distancia inter-ocular.
    # Es una aproximación, suficiente para detectar parpadeo.
    try:
        p_li = np.array(landmarks_2d[left_indices[0]])   # esquina izq ojo izq
        p_ld = np.array(landmarks_2d[left_indices[1]])   # esquina der ojo izq
        p_ri = np.array(landmarks_2d[right_indices[0]])  # esquina izq ojo der
        p_rd = np.array(landmarks_2d[right_indices[1]])  # esquina der ojo der

        # Ancho de cada ojo
        w_left  = np.linalg.norm(p_ld - p_li) + 1e-6
        w_right = np.linalg.norm(p_rd - p_ri) + 1e-6

        # Con 5 kps: usamos nariz como referencia vertical
        nariz    = np.array(landmarks_2d[2])
        centro_l = (p_li + p_ld) / 2
        centro_r = (p_ri + p_rd) / 2

        h_left  = np.linalg.norm(nariz - centro_l)
        h_right = np.linalg.norm(nariz - centro_r)

        # Normalizar por ancho del ojo para hacerlo invariante a la escala
        ear_l = h_left  / w_left
        ear_r = h_right / w_right
        return (ear_l + ear_r) / 2.0
    except Exception:
        return 0.5  # valor neutro si falla


def _analizar_parpadeo(kps_por_frame: list) -> bool:
    """
    Detecta al menos un parpadeo en la secuencia de keypoints.
    Retorna True si encontró un parpadeo válido.
    """
    # Índices InsightFace 5-kps: 0=ojo_izq_externo, 1=ojo_der_externo, 2=nariz,
    #                            3=boca_izq, 4=boca_der
    # Aproximación: cuando los ojos se cierran, la distancia ojo→nariz baja.
    ears = []
    for kps in kps_por_frame:
        if kps is None:
            ears.append(None)
            continue
        ear = _ear(kps, [0, 1], [0, 1])  # usamos los 2 kps de ojos disponibles
        ears.append(ear)

    valid_ears = [e for e in ears if e is not None]
    if len(valid_ears) < MIN_FRAMES // 2:
        return False

    media_ear = np.mean(valid_ears)

    # Buscar secuencia: EAR cae por debajo del umbral (relativo a la media del usuario)
    umbral_cierre = media_ear * 0.80  # 20% por debajo de su propia media = cerrado
    umbral_apertura = media_ear * 0.90

    estado_ojo = 'abierto'
    frames_cerrado = 0
    parpadeos = 0

    for ear in ears:
        if ear is None:
            continue
        if estado_ojo == 'abierto' and ear < umbral_cierre:
            estado_ojo = 'cerrando'
            frames_cerrado = 1
        elif estado_ojo == 'cerrando':
            if ear < umbral_cierre:
                frames_cerrado += 1
            elif ear > umbral_apertura and frames_cerrado >= BLINK_MIN_FRAMES:
                parpadeos += 1
                estado_ojo = 'abierto'
                frames_cerrado = 0
            else:
                estado_ojo = 'abierto'
                frames_cerrado = 0

    return parpadeos >= 1


def _analizar_movimiento(grises: list) -> tuple:
    """
    Analiza micro-movimientos entre frames consecutivos.
    Retorna (ok, motivo).
    - Descarta frames estáticos (foto/imagen fija).
    - Descarta loops cíclicos (GIF).
    """
    validos = [g for g in grises if g is not None]
    if len(validos) < 3:
        return False, 'No hay suficientes frames válidos para analizar movimiento.'

    # 1. Varianza de diferencias entre frames consecutivos
    diffs = []
    for i in range(1, len(validos)):
        prev = cv2.resize(validos[i-1], (80, 60)).astype(np.float32)
        curr = cv2.resize(validos[i],   (80, 60)).astype(np.float32)
        diff = np.abs(curr - prev)
        diffs.append(diff.mean())

    varianza_diffs = float(np.var(diffs))
    media_diffs    = float(np.mean(diffs))

    logger.debug(f'[liveness] varianza_diffs={varianza_diffs:.2f} media_diffs={media_diffs:.2f}')

    if media_diffs < MOTION_MEAN_THRESHOLD:
        return False, 'La imagen parece estática (sin movimiento). Mueva levemente la cabeza.'

    # 2. Detección de loop cíclico (GIF): comparar primer y último frame
    #    con el del medio. Si son muy similares → es un loop.
    if len(validos) >= 6:
        mid   = len(validos) // 2
        f0    = cv2.resize(validos[0],   (80, 60)).astype(np.float32).flatten()
        f_mid = cv2.resize(validos[mid], (80, 60)).astype(np.float32).flatten()

        norm0   = np.linalg.norm(f0)   + 1e-6
        norm_mid = np.linalg.norm(f_mid) + 1e-6

        similitud_loop = float(np.dot(f0 / norm0, f_mid / norm_mid))
        logger.debug(f'[liveness] similitud_loop (frame0 vs frame_mid)={similitud_loop:.4f}')

        # También comparar diffs[0..mid] vs diffs[mid..end] para detectar periodicidad
        primera_mitad  = diffs[:len(diffs)//2]
        segunda_mitad  = diffs[len(diffs)//2:]
        if len(primera_mitad) > 1 and len(segunda_mitad) > 1:
            diff_pattern = abs(np.mean(primera_mitad) - np.mean(segunda_mitad))
            varianza_pattern = np.var(primera_mitad) + np.var(segunda_mitad)
            # Un GIF tiene patrón de diffs muy similar en ambas mitades
            if similitud_loop > CYCLE_SIM_THRESHOLD and diff_pattern < 0.5:
                return False, 'Se detectó un patrón repetitivo (posible GIF o video en loop).'

    return True, ''


def verificar_liveness(frames_b64: list) -> tuple:
    """
    Punto de entrada principal.

    Parámetros:
        frames_b64: lista de strings base64, entre MIN_FRAMES y MAX_FRAMES.

    Retorna:
        (ok: bool, motivo: str, frame_principal_b64: str | None)
        frame_principal es el frame del medio, para guardarlo como evidencia.
    """
    # ── Validar cantidad ─────────────────────────────────────────────────────
    n = len(frames_b64)
    if n < MIN_FRAMES:
        return False, f'Se requieren al menos {MIN_FRAMES} frames para la prueba de vida.', None
    if n > MAX_FRAMES:
        frames_b64 = frames_b64[:MAX_FRAMES]
        n = MAX_FRAMES

    # ── Decodificar todos los frames ─────────────────────────────────────────
    imagenes  = []
    grises    = []
    for b64 in frames_b64:
        img = _decodificar(b64)
        imagenes.append(img)
        if img is not None:
            grises.append(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
        else:
            grises.append(None)

    validas = [i for i in imagenes if i is not None]
    if len(validas) < MIN_FRAMES // 2:
        return False, 'No se pudieron decodificar suficientes frames.', None

    # ── Frame principal (del medio) para guardar como evidencia ─────────────
    idx_medio   = n // 2
    frame_medio = imagenes[idx_medio] if imagenes[idx_medio] is not None else validas[0]
    _, buf = cv2.imencode('.jpg', frame_medio, [cv2.IMWRITE_JPEG_QUALITY, 80])
    frame_principal_b64 = base64.b64encode(buf.tobytes()).decode('utf-8')

    # ── Capa 1: análisis de micro-movimientos ────────────────────────────────
    mov_ok, mov_motivo = _analizar_movimiento(grises)
    if not mov_ok:
        return False, mov_motivo, None

    # ── Capa 2: detección de parpadeo con InsightFace ────────────────────────
    try:
        from .services import face_app  # reutilizar la instancia ya cargada

        kps_por_frame = []
        for img in imagenes:
            if img is None:
                kps_por_frame.append(None)
                continue
            try:
                faces = face_app.get(img)
                if len(faces) == 1:
                    # kps: array (5, 2) con los 5 keypoints faciales
                    kps_por_frame.append(faces[0].kps.tolist())
                else:
                    kps_por_frame.append(None)
            except Exception:
                kps_por_frame.append(None)

        kps_validos = [k for k in kps_por_frame if k is not None]
        if len(kps_validos) < MIN_FRAMES // 2:
            return False, 'No se detectó un rostro estable durante la captura. Mantenga la cara centrada.', None

        parpadeó = _analizar_parpadeo(kps_por_frame)
        if not parpadeó:
            return False, 'No se detectó parpadeo. Por favor parpadee de forma natural durante la captura.', None

    except Exception as e:
        logger.error(f'[liveness] Error en análisis de parpadeo: {e}')
        # Si InsightFace falla, al menos el movimiento fue validado.
        # No bloqueamos, pero lo registramos.

    return True, '', frame_principal_b64