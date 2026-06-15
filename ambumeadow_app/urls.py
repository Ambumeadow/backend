from django.urls import path
from . import views
from .api_views.auth import *
from .api_views.profile import *
from .api_views.notifications import *
from .api_views.ambulance import *
from .api_views.hospital import *
from .api_views.merchandise_store import *
from .api_views.doctor import *
from .api_views.appointment import *
from .api_views.admin import *
from .api_views.admin_staffs import *
from .api_views.driver import *
from .api_views.user import *


urlpatterns = [
    path('', views.index, name='index'),
    path('send_test_email/', send_test_email, name='send_test_email'),
    path('refresh_token/', refresh_token, name='refresh_token'),
    path('signin/', signin, name='signin'),
    path('staff_signin/', staff_signin, name='staff_signin'),
    path('signup/', signup, name='signup'),
    path('staff_signup/', staff_signup, name='staff_signup'),
    path('delete_account/', delete_account, name='delete_account'),
    path('verify_email/', verify_email, name='verify_email'),
    path('request_reset/', request_reset, name='request_reset'),
    path('reset_password/', reset_password, name='reset_password'),
    path('auth_check/', auth_check, name='auth_check'),

    path('get_user_notifications/', get_user_notifications, name='get_user_notifications'),
    path('update_user_profile/', update_user_profile, name='update_user_profile'),
    path('get_messages/<int:doctor_id>/', get_messages, name='get_messages'),
    path('send_message/', send_message, name='send_message'),
    path("get_patient_summary/", get_patient_summary, name="get_patient_summary"),
    path("get_medical_records/", get_medical_records, name="get_medical_records"),
    path("create_medical_record/",create_medical_record, name="create_medical_record"),
    path("get_user_subscription/", get_user_subscription, name="get_user_subscription"),
    path("get_packages/", get_packages, name="get_packages"),
    path("subscribe_package/", subscribe_package, name="subscribe_package"),

    path('add_ambulance/', add_ambulance, name='add_ambulance'),
    path('get_all_ambulances/', get_all_ambulances, name='get_all_ambulances'),
    path('get_nearest_ambulances/', get_nearest_ambulances, name='get_nearest_ambulances'),
    path('delete_ambulance/', delete_ambulance, name='delete_ambulance'),
    path('book_ambulance/', book_ambulance, name="book_ambulance"),
    path('toggle_ambulance_status/', toggle_ambulance_status, name='toggle_ambulance_status'),

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
    path('get_all_doctors/', get_all_doctors, name='get_all_doctors'),
    path('delete_user/', delete_user, name='delete_user'),
    path('toggle_user_status/', toggle_user_status, name='toggle_user_status'),
    path('get_all_staffs/', get_all_staffs, name='get_all_staffs'),
    path('delete_staff/', delete_staff, name='delete_staff'),
    path('toggle_staff_status/', toggle_staff_status, name='toggle_staff_status'),

    # driver apis
    path('driver_signup/', driver_signup, name='driver_signup'),
    path('get_drivers/<int:hospital_id>/', get_drivers, name='get_drivers'),

    # user apis
    path('send_expo_token/<str:expo_token>/', send_expo_token, name='send_expo_token'),

    # appointment apis
    path('get_my_appointments/', get_my_appointments, name='get_my_appointments'),

]