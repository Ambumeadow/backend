from django.urls import path
from . import views
from .api_views.auth import signin, signup, staff_signin, staff_signup, verify_phone, delete_account, request_password_reset
from .api_views.profile import update_user_profile
from .api_views.notifications import get_user_notifications
from .api_views.ambulance import add_ambulance, get_nearest_ambulances
from .api_views.hospital import  add_hospital, get_all_hospitals
from .api_views.merchandise_store import add_product, get_all_products, update_product_stock, create_order
from .api_views.doctor import get_active_doctors


urlpatterns = [
    path('', views.index, name='index'),
    
    path('signin/', signin, name='signin'),
    path('staff_signin/', staff_signin, name='staff_signin'),
    path('signup/', signup, name='signup'),
    path('staff_signup/', staff_signup, name='staff_signup'),
    path('verify_phone/', verify_phone, name='verify_phone'),
    path('delete_account/', delete_account, name='delete_account'),
    path('request_password_reset/', request_password_reset, name='request_password_reset'),

    path('get_user_notifications/<int:user_id>/', get_user_notifications, name='get_user_notifications'),
    path('update_user_profile/', update_user_profile, name='update_user_profile'),

    path('add_ambulance/', add_ambulance, name='add_ambulance'),
    path('get_nearest_ambulances/', get_nearest_ambulances, name='get_nearest_ambulances'),

    path('add_hospital/', add_hospital, name='add_hospital'),
    path('get_all_hospitals/', get_all_hospitals, name='get_all_hospitals'),

    path('add_product/', add_product, name='add_product'),
    path('get_all_products/', get_all_products, name='get_all_products'),
    path('update_product_stock/', update_product_stock, name='update_product_stock'),
    path('create_order/', create_order, name='create_order'),

    path('get_active_doctors/', get_active_doctors, name='get_active_doctors'),

]