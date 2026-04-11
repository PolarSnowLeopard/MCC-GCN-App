from django.conf import settings
from django.db import models


class PredictionTask(models.Model):
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('running', '运行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    TASK_TYPE_CHOICES = [
        ('single', '单次预测'),
        ('batch', '批量筛选'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prediction_tasks')
    model = models.ForeignKey('ml_models.MLModel', on_delete=models.CASCADE)
    task_type = models.CharField(max_length=10, choices=TASK_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    input_data = models.JSONField()
    result = models.JSONField(null=True, blank=True)
    celery_task_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'prediction_tasks'
        ordering = ['-created_at']


class FinetuneTask(models.Model):
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('running', '运行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='finetune_tasks')
    base_model = models.ForeignKey('ml_models.MLModel', on_delete=models.CASCADE)
    result_model = models.ForeignKey('ml_models.MLModel', null=True, blank=True, on_delete=models.SET_NULL, related_name='finetune_source')
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    training_file = models.FileField(upload_to='finetune_data/')
    config = models.JSONField(default=dict)
    log = models.TextField(blank=True)
    celery_task_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'finetune_tasks'
        ordering = ['-created_at']
