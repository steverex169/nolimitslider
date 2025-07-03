from django.urls import path
from . import views

urlpatterns = [
    path('', views.carousel_view, name='carousel'),
    path('superadmib/', views.superadmib_view, name='superadmib'),
    path('superadmib/delete/<int:image_id>/', views.delete_carousel_image, name='delete_carousel_image'),
]
