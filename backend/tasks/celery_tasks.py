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
    import os
    from django.conf import settings
    from .models import FinetuneTask
    from ml_models.models import MLModel
    from .services.finetune import run_finetune as do_finetune

    task = FinetuneTask.objects.get(id=task_id)
    task.status = 'running'
    task.save(update_fields=['status'])
    try:
        base_model = task.base_model
        output_dir = os.path.join(settings.MEDIA_ROOT, 'models')
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f'ft_{task.id}_{task.name}.pth'
        output_path = os.path.join(output_dir, output_filename)

        config = {
            **task.config,
            'num_classes': base_model.num_classes,
            'train_layers': task.config.get('train_layers', 3),
            'weight_decay': task.config.get('weight_decay', 0.3),
        }

        result = do_finetune(
            base_model_path=base_model.model_file.path,
            csv_path=task.training_file.path,
            output_path=output_path,
            config=config,
        )

        new_model = MLModel.objects.create(
            user=task.user,
            name=task.name,
            description=f'Fine-tuned from {base_model.name}. Val BACC: {result["best_val_bacc"]}',
            model_type='finetuned',
            base_model=base_model,
            num_classes=base_model.num_classes,
            status='draft',
        )
        new_model.model_file.name = f'models/{output_filename}'
        new_model.save(update_fields=['model_file'])

        task.result_model = new_model
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.log = result['log']
    except Exception:
        import traceback
        task.status = 'failed'
        task.log = traceback.format_exc()
    task.save()
