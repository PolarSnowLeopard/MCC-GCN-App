from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ml_models.models import MLModel
from .models import PredictionTask, FinetuneTask
from .serializers import (
    PredictionTaskSerializer,
    PredictionCreateSerializer,
    BatchPredictionCreateSerializer,
    FinetuneTaskSerializer,
    FinetuneCreateSerializer,
)
from .services.predict import predict_single as run_predict
from .celery_tasks import run_batch_prediction, run_finetune


@api_view(['POST'])
def predict_single(request):
    serializer = PredictionCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    model_obj = MLModel.objects.get(id=data['model_id'])

    try:
        result = run_predict(
            data['api_smiles'],
            data['coformer_smiles'],
            model_path=model_obj.model_file.path,
            num_classes=model_obj.num_classes,
            is_large=model_obj.is_large,
        )
    except ValueError as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    task = PredictionTask.objects.create(
        user=request.user,
        model=model_obj,
        task_type='single',
        status='completed',
        input_data={'api_smiles': data['api_smiles'], 'coformer_smiles': data['coformer_smiles']},
        result=result,
        completed_at=timezone.now(),
    )
    return Response({
        'task': PredictionTaskSerializer(task).data,
        'result': result,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def predict_batch(request):
    serializer = BatchPredictionCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    model_obj = MLModel.objects.get(id=data['model_id'])
    task = PredictionTask.objects.create(
        user=request.user,
        model=model_obj,
        task_type='batch',
        status='pending',
        input_data={'pairs': data['pairs']},
    )
    celery_result = run_batch_prediction.delay(
        task.id,
        model_obj.model_file.path,
        model_obj.num_classes,
        model_obj.is_large,
    )
    task.celery_task_id = celery_result.id
    task.save(update_fields=['celery_task_id'])

    return Response({
        'task_id': task.id,
        'celery_task_id': celery_result.id,
        'status': 'pending',
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def finetune_create(request):
    serializer = FinetuneCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    base_model = MLModel.objects.get(id=data['base_model_id'])
    task = FinetuneTask.objects.create(
        user=request.user,
        base_model=base_model,
        name=data['name'],
        status='pending',
        training_file=data['training_file'],
        config={
            'epochs': data['epochs'],
            'batch_size': data['batch_size'],
            'learning_rate': data['learning_rate'],
        },
    )
    celery_result = run_finetune.delay(task.id)
    task.celery_task_id = celery_result.id
    task.save(update_fields=['celery_task_id'])

    return Response({
        'task_id': task.id,
        'celery_task_id': celery_result.id,
        'status': 'pending',
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def task_list(request):
    qs = PredictionTask.objects.filter(user=request.user)
    task_type = request.query_params.get('type')
    if task_type in ('single', 'batch'):
        qs = qs.filter(task_type=task_type)
    serializer = PredictionTaskSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def task_detail(request, pk):
    task = PredictionTask.objects.get(id=pk, user=request.user)
    return Response(PredictionTaskSerializer(task).data)


@api_view(['GET'])
def finetune_list(request):
    qs = FinetuneTask.objects.filter(user=request.user)
    serializer = FinetuneTaskSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def finetune_detail(request, pk):
    task = FinetuneTask.objects.get(id=pk, user=request.user)
    return Response(FinetuneTaskSerializer(task).data)
