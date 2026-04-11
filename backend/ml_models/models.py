from django.conf import settings
from django.db import models


class MLModel(models.Model):
    TYPE_CHOICES = [
        ('pretrained', '预训练模型'),
        ('finetuned', '微调模型'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    model_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    base_model = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='derived_models')
    model_file = models.FileField(upload_to='models/')
    is_large = models.BooleanField(default=True)
    num_classes = models.IntegerField(default=4)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ml_models'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_model_type_display()})"
