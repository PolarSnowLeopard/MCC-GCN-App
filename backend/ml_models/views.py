from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import MLModel
from .serializers import MLModelSerializer


class MLModelViewSet(ModelViewSet):
    serializer_class = MLModelSerializer

    def get_queryset(self):
        return MLModel.objects.filter(
            Q(user=self.request.user) | Q(is_builtin=True) | Q(status='published')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.is_builtin:
            raise PermissionDenied('内置模型不可删除')
        instance.delete()

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        instance = self.get_object()
        if instance.user != request.user:
            raise PermissionDenied('只能发布自己的模型')
        instance.status = 'published'
        instance.save(update_fields=['status'])
        return Response(MLModelSerializer(instance).data)
