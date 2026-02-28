import base64
import logging

from .config import FACE_CONFIG
from .loader import get_model

logger = logging.getLogger(__name__)


def _b64_to_image(image_b64: str):
    """Convierte base64 (con o sin data URL prefix) a numpy array BGR."""
    import cv2
    import numpy as np

    if ',' in image_b64:
        image_b64 = image_b64.split(',', 1)[1]
    image_bytes = base64.b64decode(image_b64)
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError('No se pudo decodificar la imagen')
    return img


def extract_embedding(image_b64: str) -> dict:
    """
    Extrae un embedding ArcFace de 512 dimensiones a partir de una imagen en base64.

    Returns:
        {
            'success': bool,
            'embedding': list[float] | None,  # 512 valores normalizados L2
            'confidence': float | None,
            'errors': list[str],
        }
    """
    import numpy as np

    try:
        img = _b64_to_image(image_b64)
    except Exception as e:
        return {'success': False, 'embedding': None, 'confidence': None, 'errors': [str(e)]}

    try:
        model = get_model()
        faces = model.get(img)
    except Exception as e:
        return {'success': False, 'embedding': None, 'confidence': None, 'errors': [f'Error en modelo: {e}']}

    if not faces:
        return {'success': False, 'embedding': None, 'confidence': None, 'errors': ['No se detectó ningún rostro en la imagen']}

    if len(faces) > 1:
        # Usar el rostro más grande (mayor área bbox)
        faces = sorted(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]), reverse=True)

    face = faces[0]
    confidence = float(face.det_score)

    if confidence < FACE_CONFIG['MIN_CONFIDENCE']:
        return {
            'success': False,
            'embedding': None,
            'confidence': confidence,
            'errors': [f'Calidad de imagen insuficiente (confianza: {confidence:.2f}, mínimo: {FACE_CONFIG["MIN_CONFIDENCE"]})'],
        }

    embedding = face.embedding.astype(np.float32)
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm

    return {
        'success': True,
        'embedding': embedding.tolist(),
        'confidence': confidence,
        'errors': [],
    }


def create_template(embeddings: list, confidences: list = None) -> list:
    """
    Genera un vector template normalizado (L2=1) a partir de 1-5 embeddings.
    Usa promedio ponderado por confianza si se proporcionan confidences.

    Returns: list[float] de 512 dimensiones, norma=1.
    """
    import numpy as np

    if not embeddings:
        raise ValueError('Se necesita al menos un embedding')

    vecs = np.array(embeddings, dtype=np.float32)

    if confidences and len(confidences) == len(embeddings):
        weights = np.array(confidences, dtype=np.float32)
        weights = weights / weights.sum()
        template = np.average(vecs, axis=0, weights=weights)
    else:
        template = np.mean(vecs, axis=0)

    norm = np.linalg.norm(template)
    if norm > 0:
        template = template / norm

    return template.tolist()


def cosine_similarity(v1: list, v2: list) -> float:
    """
    Similitud coseno entre dos vectores normalizados.
    Rango: [-1.0, 1.0]. Valores >= 0.75 indican match.
    """
    import numpy as np

    a = np.array(v1, dtype=np.float32)
    b = np.array(v2, dtype=np.float32)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))
