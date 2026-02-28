import json
import logging

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from audit.models import AuditLog
from .face_engine.config import FACE_CONFIG
from .face_engine.embedder import cosine_similarity, create_template, extract_embedding

logger = logging.getLogger(__name__)


class EnrollView(APIView):
    """
    POST /api/auth/biometrics/enroll/
    Registra el rostro del inventarista usando 1-5 fotos.
    Body: { "images": ["base64...", ...] }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.user_type != 'inventarista':
            return Response(
                {'error': 'Solo los inventaristas pueden registrar su rostro'},
                status=status.HTTP_403_FORBIDDEN,
            )

        images = request.data.get('images', [])
        if not images:
            return Response({'error': 'Se requiere al menos una imagen'}, status=status.HTTP_400_BAD_REQUEST)

        max_photos = FACE_CONFIG['MAX_ENROLLMENT_PHOTOS']
        if len(images) > max_photos:
            images = images[:max_photos]

        embeddings = []
        confidences = []
        errors = []

        for i, img_b64 in enumerate(images):
            result = extract_embedding(img_b64)
            if result['success']:
                embeddings.append(result['embedding'])
                confidences.append(result['confidence'])
            else:
                errors.append(f'Foto {i + 1}: {"; ".join(result["errors"])}')

        if not embeddings:
            return Response(
                {'error': 'Ninguna foto fue válida', 'details': errors},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        template = create_template(embeddings, confidences)
        user.face_encoding = json.dumps(template)
        user.face_enrolled_at = timezone.now()
        user.save(update_fields=['face_encoding', 'face_enrolled_at'])

        AuditLog.log_action(
            action='biometric_enroll',
            user=user,
            account=user.account,
            description=f'Rostro registrado con {len(embeddings)} foto(s)',
            ip_address=request.META.get('REMOTE_ADDR'),
        )

        return Response({
            'enrolled': True,
            'photos_used': len(embeddings),
            'warnings': errors,
        }, status=status.HTTP_200_OK)


class VerifyView(APIView):
    """
    POST /api/auth/biometrics/verify/
    Verifica si la foto enviada corresponde al inventarista autenticado.
    Body: { "image": "base64..." }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.user_type != 'inventarista':
            return Response(
                {'error': 'Solo los inventaristas pueden verificar su rostro'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not user.face_encoding:
            return Response(
                {'error': 'not_enrolled', 'message': 'No tienes un rostro registrado. Ve a Configuración → Verificación Biométrica.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        image_b64 = request.data.get('image')
        if not image_b64:
            return Response({'error': 'Se requiere el campo "image"'}, status=status.HTTP_400_BAD_REQUEST)

        result = extract_embedding(image_b64)
        if not result['success']:
            return Response(
                {'error': 'No se pudo procesar la imagen', 'details': result['errors']},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        stored_template = json.loads(user.face_encoding)
        similarity = cosine_similarity(result['embedding'], stored_template)
        threshold = FACE_CONFIG['VERIFICATION_THRESHOLD']
        match = similarity >= threshold

        if not match:
            AuditLog.log_action(
                action='biometric_verify_fail',
                user=user,
                account=user.account,
                description=f'Verificación facial fallida (similitud: {similarity:.3f})',
                ip_address=request.META.get('REMOTE_ADDR'),
            )

        return Response({
            'match': match,
            'similarity': round(similarity, 4),
            'threshold': threshold,
        })


class StatusView(APIView):
    """
    GET /api/auth/biometrics/status/
    Retorna si el usuario tiene su rostro registrado.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        enrolled = bool(user.face_encoding)
        enrolled_at = getattr(user, 'face_enrolled_at', None)
        return Response({
            'enrolled': enrolled,
            'enrolled_at': enrolled_at.isoformat() if enrolled_at else None,
        })
