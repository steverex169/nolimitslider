from django.urls import path
from . import views

urlpatterns = [
    path('', views.carousel_view, name='carousel'),
    path('carousel/', views.carousel_view, name='carousel'),
    path('superadmin/', views.superadmin_view, name='superadmin'),
    path('superadmin/delete/<int:image_id>/', views.delete_carousel_image, name='delete_carousel_image'),
    path('carousel/edit/<int:image_id>/', views.edit_carousel_image, name='edit_carousel_image'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('preview-terms/', views.preview_terms_view, name='preview_terms'),
    path('terms-conditions/', views.general_termscondition, name='terms-conditions'),
    path('about-us/', views.general_AboutUs, name='about-us'),
    path('carousel/image/<int:image_id>/', views.carousel_image_detail, name='carousel_image_detail'),

]
