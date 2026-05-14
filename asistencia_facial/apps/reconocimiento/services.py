import numpy as np
import cv2
import base64
from insightface.app import FaceAnalysis


# Inicializar InsightFace una sola vez cuando arranca el servidor
face_app = FaceAnalysis(
    name='buffalo_l',
    providers=['CPUExecutionProvider']
)
face_app.prepare(ctx_id=0, det_size=(640, 640))


def decodificar_imagen(imagen_base64):
    try:
        if ',' in imagen_base64:
            imagen_base64 = imagen_base64.split(',')[1]

        imagen_base64 = imagen_base64.strip().replace('\n', '').replace('\r', '').replace(' ', '')

        padding = 4 - len(imagen_base64) % 4
        if padding != 4:
            imagen_base64 += '=' * padding

        imagen_bytes = base64.b64decode(imagen_base64)
        imagen_array = np.frombuffer(imagen_bytes, dtype=np.uint8)
        imagen = cv2.imdecode(imagen_array, cv2.IMREAD_COLOR)

        if imagen is None:
            return None

        # Redimensionar si es muy pequeña para mejorar detección
        alto, ancho = imagen.shape[:2]
        if ancho < 640 or alto < 640:
            factor = 640 / min(ancho, alto)
            imagen = cv2.resize(imagen, None, fx=factor, fy=factor,
                                interpolation=cv2.INTER_LINEAR)


        # Mejorar brillo y contraste automáticamente
        imagen = cv2.convertScaleAbs(imagen, alpha=1.2, beta=10)

        return imagen
    except Exception as e:
        print(f'Error decodificando imagen: {e}')
        return None


def generar_embedding(imagen_base64):
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

    embedding = face.embedding.astype(np.float64)
    norma = np.linalg.norm(embedding)
    if norma == 0:
        return None, 'Embedding inválido (norma cero)'

    embedding = embedding / norma

    print(f"[generar_embedding] det_score={det_score:.3f} | norma={np.linalg.norm(embedding):.6f} | dim={embedding.shape[0]}")

    return embedding.tolist(), None


def generar_embedding_promedio(imagenes_base64):
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

    embedding_promedio = np.mean(np.array(embeddings, dtype=np.float64), axis=0)
    norma = np.linalg.norm(embedding_promedio)

    if norma == 0:
        return None, 'Embedding promedio inválido (norma cero)'

    embedding_promedio = embedding_promedio / norma

    print(f"[generar_embedding_promedio] imagenes={len(imagenes_base64)} | norma_final={np.linalg.norm(embedding_promedio):.6f}")

    return embedding_promedio.tolist(), None


def comparar_embeddings(embedding1, embedding2, umbral):
    e1 = np.array(embedding1, dtype=np.float64)
    e2 = np.array(embedding2, dtype=np.float64)

    norm1 = np.linalg.norm(e1)
    norm2 = np.linalg.norm(e2)

    print(f"[comparar_embeddings] dim_capturado={e1.shape[0]} | dim_bd={e2.shape[0]} | norma_cap={norm1:.6f} | norma_bd={norm2:.6f} | umbral={umbral}")

    if norm1 == 0 or norm2 == 0:
        print("[comparar_embeddings] ERROR: norma cero")
        return False, 0.0

    if e1.shape[0] != e2.shape[0]:
        print(f"[comparar_embeddings] ERROR: dimensiones incompatibles ({e1.shape[0]} vs {e2.shape[0]})")
        return False, 0.0

    # Re-normalizar para absorber errores de precisión al serializar/deserializar desde la BD
    e1 = e1 / norm1
    e2 = e2 / norm2

    similitud = float(np.dot(e1, e2))

    print(f"[comparar_embeddings] similitud={similitud:.4f} | verificado={similitud >= umbral}")

    return similitud >= umbral, similitud