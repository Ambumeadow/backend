from django.urls import path
from . import views
from .api_views.auth import signin, signup, staff_signin, staff_signup, verify_phone, delete_account, request_password_reset, refresh_token
from .api_views.profile import update_user_profile
from .api_views.notifications import get_user_notifications
from .api_views.ambulance import add_ambulance, get_nearest_ambulances
from .api_views.hospital import  add_hospital, get_all_hospitals
from .api_views.merchandise_store import add_product, get_all_products, update_product_stock, create_order
from .api_views.doctor import get_active_doctors
from .api_views.appointment import  schedule_care
from .api_views.admin import get_all_users, delete_user, toggle_user_status
from .api_views.admin_staffs import get_all_staffs, delete_staff, toggle_staff_status


urlpatterns = [
    path('', views.index, name='index'),

    path('refresh_token/', refresh_token, name='refresh_token'),
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

    path('schedule_care/', schedule_care, name='schedule_care'),

    # admin apis
    path('get_all_users/', get_all_users, name='get_all_users'),
    path('delete_user/', delete_user, name='delete_user'),
    path('toggle_user_status/', toggle_user_status, name='toggle_user_status'),
    path('get_all_staffs/', get_all_staffs, name='get_all_staffs'),
    path('delete_staff/', delete_staff, name='delete_staff'),
    path('toggle_staff_status/', toggle_staff_status, name='toggle_staff_status'),

]