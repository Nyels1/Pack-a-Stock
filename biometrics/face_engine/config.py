FACE_CONFIG = {
    'MODEL_NAME': 'buffalo_l',
    'EMBEDDING_SIZE': 512,
    # Umbral de confianza de detección (webcam tiene menor calidad que foto profesional)
    'MIN_CONFIDENCE': 0.80,
    # Similitud coseno mínima para considerar un match válido
    'VERIFICATION_THRESHOLD': 0.75,
    'MAX_ENROLLMENT_PHOTOS': 5,
    'MIN_ENROLLMENT_PHOTOS': 1,
}
