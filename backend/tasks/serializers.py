from rest_framework import serializers
from .models import PredictionTask, FinetuneTask


class PredictionTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionTask
        fields = '__all__'
        read_only_fields = ['user', 'status', 'result', 'celery_task_id', 'created_at', 'completed_at']


class PredictionCreateSerializer(serializers.Serializer):
    model_id = serializers.IntegerField()
    api_smiles = serializers.CharField()
    coformer_smiles = serializers.CharField()


class BatchPredictionCreateSerializer(serializers.Serializer):
    model_id = serializers.IntegerField()
    pairs = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
    )


class FinetuneTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinetuneTask
        fields = '__all__'
        read_only_fields = ['user', 'status', 'result_model', 'log', 'celery_task_id', 'created_at', 'completed_at']


class FinetuneCreateSerializer(serializers.Serializer):
    base_model_id = serializers.IntegerField()
    name = serializers.CharField()
    training_file = serializers.FileField()
    epochs = serializers.IntegerField(default=50)
    batch_size = serializers.IntegerField(default=16)
    learning_rate = serializers.FloatField(default=3e-4)
