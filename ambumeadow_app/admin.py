from django.contrib import admin
from .models import User, Notification, Staff, StaffNotification, Patient, MedicalRecord, Ambulance, Hospital, Product, ProductOrder, CareAppointment, DriverNotification


admin.site.register(User)
admin.site.register(Notification)
admin.site.register(Staff)
admin.site.register(StaffNotification)
admin.site.register(DriverNotification)
admin.site.register(Patient)
admin.site.register(MedicalRecord)
admin.site.register(Ambulance)
admin.site.register(Hospital)
admin.site.register(Product)
admin.site.register(ProductOrder)
admin.site.register(CareAppointment)
