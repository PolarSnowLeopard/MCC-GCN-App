from rest_framework.routers import DefaultRouter
from .views import MLModelViewSet

router = DefaultRouter()
router.register('', MLModelViewSet, basename='mlmodel')

urlpatterns = router.urls
