from django.db import models
from django.utils import timezone

# -----------------------------
# 1. User Model
# -----------------------------
class User(models.Model):
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.CharField(max_length=100, default="johndoe@example.com")
    agreed = models.BooleanField(default=False)
    firebase_uid = models.CharField(max_length=256, default="@Ambumeadow2025")
    current_lat = models.FloatField(null=True, blank=True, default=0.0)
    current_lng = models.FloatField(null=True, blank=True, default=0.0)
    phone_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    expo_token = models.CharField(max_length=100, default="hsvsx92jjs")

    def __str__(self):
        return f"{self.full_name} Date joined: ({self.date_joined})"

# hospital model
class Hospital(models.Model):
    hospital_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, default="")
    phone_number = models.CharField(max_length=20, unique=True)
    emergency_contact = models.CharField(max_length=20, default="")
    latitude = models.FloatField(null=True, blank=True, default=0.0)
    longitude = models.FloatField(null=True, blank=True, default=0.0)
    date_joined = models.DateTimeField(default=timezone.now)

# driver model
class Driver(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.CharField(max_length=100, default="")
    license_number = models.CharField(max_length=50, unique=True)
    firebase_uid = models.CharField(max_length=256, default="@Ambumeadow2025")
    phone_verified = models.BooleanField(default=False)
    agreed = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    profile_image = models.URLField(blank=True, null=True, default='')
    expo_token = models.CharField(max_length=100, default="hsvsx92jjs")
    date_joined = models.DateTimeField(default=timezone.now)

# staff model
class Staff(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('superadmin', 'SuperAdmin'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('pharmacist', 'Pharmacist'),
        ('lab_technician', 'Lab Technician'),
        ('receptionist', 'Receptionist'),
        ('driver', 'Driver'),
        ('other', 'Other'),
    ]
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.CharField(max_length=100, default="johndoe@example.com")
    id_number = models.CharField(max_length=8, default='12345678')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='other')
    firebase_uid = models.CharField(max_length=256, default="@Ambumeadow2025")
    phone_verified = models.BooleanField(default=False)
    agreed = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    profile_image = models.URLField(blank=True, null=True, default='')
    expo_token = models.CharField(max_length=100, default="hsvsx92jjs")
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.full_name} Date joined: ({self.date_joined})"

# patient model link to user
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    blood_group = models.CharField(max_length=5)
    height = models.FloatField()
    weight = models.FloatField()
    under_medication = models.BooleanField(default=False)
    ward = models.CharField(max_length=100)
    emergency_contact = models.CharField(max_length=20)
    insurance_provider = models.CharField(max_length=100)
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.full_name} Under medication: ({self.under_medication})"

# medical record model
class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    diagnosis = models.TextField()
    prescription = models.TextField()
    notes = models.TextField()

    def __str__(self):
        return f"{self.patient.user.full_name} Date: ({self.date})"

# staff notification model
class StaffNotification(models.Model):
    TYPES = [
        ('appointment','Appointment'),
        ('system','System'),
        ('prescription','Prescription'),
        ('update','Update'),
        ('order','Order'),
    ]
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    message_type = models.CharField(max_length=20, choices=TYPES, default='update')
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.staff.full_name} {self.message_type} Date: ({self.date})"

# notification model
class Notification(models.Model):
    TYPES = [
        ('appointment','Appointment'),
        ('system','System'),
        ('prescription','Prescription'),
        ('update','Update'),
        ('order','Order'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    message_type = models.CharField(max_length=20, choices=TYPES, default='update')
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.full_name} {self.message_type} Date: ({self.date})"

# ambulance model
class Ambulance(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    plate_number = models.CharField(max_length=20, unique=True)
    driver_phone = models.CharField(max_length=20)
    is_available = models.BooleanField(default=True)
    current_lat = models.FloatField(null=True, blank=True, default=0.0)
    current_lng = models.FloatField(null=True, blank=True, default=0.0)
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Ambulance {self.plate_number} Driver: {self.driver_name}"
