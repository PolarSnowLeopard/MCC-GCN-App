from celery import shared_task
from django.utils import timezone


@shared_task
def run_batch_prediction(task_id, model_path, num_classes):
    from .models import PredictionTask
    from .services.predict import predict_batch

    task = PredictionTask.objects.get(id=task_id)
    task.status = 'running'
    task.save(update_fields=['status'])
    try:
        results = predict_batch(
            task.input_data['pairs'],
            model_path=model_path,
            num_classes=num_classes,
        )
        task.result = results
        task.status = 'completed'
        task.completed_at = timezone.now()
    except Exception as e:
        task.status = 'failed'
        task.result = {'error': str(e)}
    task.save()


@shared_task
def run_finetune(task_id):
    from .models import FinetuneTask
    import time

    task = FinetuneTask.objects.get(id=task_id)
    task.status = 'running'
    task.save(update_fields=['status'])
    try:
        # TODO: integrate real finetune pipeline
        time.sleep(5)
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.log = 'Finetune completed (mock)'
    except Exception as e:
        task.status = 'failed'
        task.log = str(e)
    task.save()
