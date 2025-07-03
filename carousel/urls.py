from django.urls import path
from .views import carousel_view

urlpatterns = [
    path('', carousel_view, name='carousel'),
]
