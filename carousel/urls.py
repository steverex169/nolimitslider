from django.urls import path
from . import views

urlpatterns = [
    path('', views.carousel_view, name='carousel'),
    path('superadmin/', views.superadmin_view, name='superadmin'),
    path('superadmin/delete/<int:image_id>/', views.delete_carousel_image, name='delete_carousel_image'),
]
