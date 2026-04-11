from django.contrib import admin
from .models import PredictionTask, FinetuneTask


@admin.register(PredictionTask)
class PredictionTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'task_type', 'status', 'created_at')
    list_filter = ('status', 'task_type')


@admin.register(FinetuneTask)
class FinetuneTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'status', 'created_at')
    list_filter = ('status',)
