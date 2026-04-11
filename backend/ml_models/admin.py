from django.contrib import admin
from .models import MLModel


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'model_type', 'created_at')
    list_filter = ('model_type',)
