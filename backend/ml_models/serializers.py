from rest_framework import serializers
from .models import MLModel


class MLModelSerializer(serializers.ModelSerializer):
    user_display = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = MLModel
        fields = '__all__'
        read_only_fields = ['user']
