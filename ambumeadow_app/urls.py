from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('verify_phone/', views.verify_phone, name='verify_phone'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('request_password_reset/', views.request_password_reset, name='request_password_reset'),
    path('get_user_notifications/<int:user_id>/', views.get_user_notifications, name='get_user_notifications'),
    path('update_user_profile/', views.update_user_profile, name='update_user_profile'),
]