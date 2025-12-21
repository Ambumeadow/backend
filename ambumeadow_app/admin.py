from django.contrib import admin
from .models import User, Notification, Staff, StaffNotification

admin.site.register(User)
admin.site.register(Notification)
admin.site.register(Staff)
admin.site.register(StaffNotification)
