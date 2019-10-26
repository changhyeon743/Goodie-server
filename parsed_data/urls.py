from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_swagger.views import get_swagger_view

router = DefaultRouter()
router.register('videos',views.VideoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('docs/',get_swagger_view(title="Goodie"),name="Goodie")
]
