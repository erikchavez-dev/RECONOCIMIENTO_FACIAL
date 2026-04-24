import numpy as np
import cv2
import base64
from insightface.app import FaceAnalysis


# det_size=(320, 320) en lugar de (640, 640):
#   - Procesa ~4x menos píxeles en la etapa de detección
#   - Para rostros centrados que ocupan la mayor parte del encuadre, la precisión
#     no se ve afectada de forma significativa
#   - El frontend ahora envía imágenes de 320×240, que coincide perfectamente
#     con este det_size sin necesidad de redimensionado adicional
face_app = FaceAnalysis(
    name='buffalo_l',
    providers=['CPUExecutionProvider']
)
face_app.prepare(ctx_id=0, det_size=(320, 320))


def decodificar_imagen(imagen_base64):
    """
    Decodifica la imagen base64 a un array de OpenCV.
    NO redimensiona ni ajusta brillo/contraste — esas operaciones
    añadían latencia sin beneficio real cuando el frontend ya envía
    la imagen a la resolución correcta (320×240).
    """
    try:
        if ',' in imagen_base64:
            imagen_base64 = imagen_base64.split(',')[1]

        imagen_base64 = imagen_base64.strip().replace('\n', '').replace('\r', '').replace(' ', '')

        # Corregir padding faltante
        padding = 4 - len(imagen_base64) % 4
        if padding != 4:
            imagen_base64 += '=' * padding

        imagen_bytes = base64.b64decode(imagen_base64)
        imagen_array = np.frombuffer(imagen_bytes, dtype=np.uint8)
        imagen = cv2.imdecode(imagen_array, cv2.IMREAD_COLOR)

        return imagen  # puede ser None si falla el decode
    except Exception as e:
        print(f'Error decodificando imagen: {e}')
        return None


def generar_embedding(imagen_base64):
    """
    Genera el embedding facial de una imagen base64.
    Valida que haya exactamente un rostro y que la calidad de detección sea
    suficiente. Normaliza el embedding para que la comparación coseno sea correcta.
    """
    imagen = decodificar_imagen(imagen_base64)
    if imagen is None:
        return None, 'No se pudo decodificar la imagen'

    try:
        faces = face_app.get(imagen)
    except Exception as e:
        print("ERROR InsightFace:", e)
        return None, 'Error procesando el rostro (modelo)'

    if len(faces) == 0:
        return None, 'No se detectó ningún rostro. Acérquese más o mejore la iluminación'

    if len(faces) > 1:
        return None, 'Se detectó más de un rostro, por favor capture solo un rostro'

    face = faces[0]
    det_score = face.det_score

    if det_score < 0.6:
        return None, f'Rostro detectado con baja calidad ({det_score:.2f}). Mejore la iluminación'

    embedding = face.embedding
    embedding = embedding / np.linalg.norm(embedding)
    return embedding.tolist(), None


def generar_embedding_promedio(imagenes_base64):
    """
    Genera un embedding promedio a partir de varias imágenes.
    Mejora la precisión del reconocimiento al representar el rostro
    en diferentes condiciones (ángulo, luz, expresión).
    """
    if len(imagenes_base64) < 2:
        return None, 'Se requieren mínimo 2 imágenes para generar embedding promedio'

    if len(imagenes_base64) > 5:
        return None, 'Se permiten máximo 5 imágenes'

    embeddings = []
    for i, imagen_base64 in enumerate(imagenes_base64):
        embedding, error = generar_embedding(imagen_base64)
        if error:
            return None, f'Error en imagen {i + 1}: {error}'
        embeddings.append(embedding)

    embedding_promedio = np.mean(embeddings, axis=0)
    norma = np.linalg.norm(embedding_promedio)
    return (embedding_promedio / norma).tolist(), None


def comparar_embeddings(embedding1, embedding2, umbral):
    """
    Similitud coseno entre dos embeddings normalizados.
    Retorna (verificado: bool, similitud: float).
    """
    e1 = np.array(embedding1)
    e2 = np.array(embedding2)

    norm1 = np.linalg.norm(e1)
    norm2 = np.linalg.norm(e2)

    if norm1 == 0 or norm2 == 0:
        return False, 0.0

    similitud = float(np.dot(e1, e2) / (norm1 * norm2))
    return similitud >= umbral, similitud