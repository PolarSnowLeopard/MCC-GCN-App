from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.predict_single),
    path('batch/', views.predict_batch),
    path('finetune/', views.finetune_create),
    path('', views.task_list),
    path('<int:pk>/', views.task_detail),
    path('finetune/list/', views.finetune_list),
    path('finetune/<int:pk>/', views.finetune_detail),
]
