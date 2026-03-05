import logging

logger = logging.getLogger(__name__)

_model_instance = None


def get_model():
    """
    Carga lazy del modelo ArcFace (Singleton).
    Detecta automáticamente CUDA vs CPU.
    """
    global _model_instance
    if _model_instance is not None:
        return _model_instance

    try:
        import insightface
        from insightface.app import FaceAnalysis

        providers = _get_providers()
        logger.info(f'Cargando modelo ArcFace con providers: {providers}')

        app = FaceAnalysis(name='buffalo_l', providers=providers)
        app.prepare(ctx_id=0, det_size=(320, 320))
        _model_instance = app
        logger.info('Modelo ArcFace cargado correctamente')
        return _model_instance

    except Exception as e:
        logger.error(f'Error cargando modelo ArcFace: {e}')
        raise


def _get_providers():
    """Detecta CUDA vs CPU y retorna la lista de providers."""
    import onnxruntime as ort
    available = ort.get_available_providers()
    if 'CUDAExecutionProvider' in available:
        return ['CUDAExecutionProvider', 'CPUExecutionProvider']
    return ['CPUExecutionProvider']
