from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet

from .models import MLModel
from .serializers import MLModelSerializer


class MLModelViewSet(ModelViewSet):
    serializer_class = MLModelSerializer

    def get_queryset(self):
        return MLModel.objects.filter(
            Q(user=self.request.user) | Q(model_type='pretrained')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.is_builtin:
            raise PermissionDenied('内置模型不可删除')
        instance.delete()
