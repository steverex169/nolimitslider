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
    path('promotions/', views.promotion, name='promotions'),
    path('promotions/promotions1/', views.promotion1, name='promotions1'),
    path('promotions/promotions2/', views.promotion2, name='promotions2'),
    path('promotions/promotions3/', views.promotion3, name='promotions3'),
    path('promotions/promotions4/', views.promotion4, name='promotions4'),
    path('promotions/promotions5/', views.promotion5, name='promotions5'),
    path('promotions/promotions6/', views.promotion6, name='promotions6'),
    path('promotions/promotions7/', views.promotion7, name='promotions7'),
    path('promotions/promotions8/', views.promotion8, name='promotions8'),
    path('promotions/promotions9/', views.promotion9, name='promotions9'),
    path('promotions/promotions10/', views.promotion10, name='promotions10'),
    path('licence/', views.licence, name='licence'),

    path('carousel/image/<int:image_id>/', views.carousel_image_detail, name='carousel_image_detail'),

]
