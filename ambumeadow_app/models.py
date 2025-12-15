from django.db import models
from django.utils import timezone

# -----------------------------
# 1. User Model
# -----------------------------
class User(models.Model):
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.CharField(max_length=100, default="johndoe@example.com")
    firebase_uid = models.CharField(max_length=256, default="@Ambumeadow2025")
    current_lat = models.FloatField(null=True, blank=True, default=0.0)
    current_lng = models.FloatField(null=True, blank=True, default=0.0)
    phone_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    profile_image = models.URLField(blank=True, null=True, default='https://res.cloudinary.com/dc68huvjj/image/upload/v1748119193/zzy3zwrius3kjrzp4ifc.png')
    date_joined = models.DateTimeField(default=timezone.now)
    expo_token = models.CharField(max_length=100, default="hsvsx92jjs")

    def __str__(self):
        return f"{self.full_name} Date joined: ({self.date_joined})"

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
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='other')
    firebase_uid = models.CharField(max_length=256, default="@Ambumeadow2025")
    phone_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    profile_image = models.URLField(blank=True, null=True, default='https://res.cloudinary.com/dc68huvjj/image/upload/v1748119193/zzy3zwrius3kjrzp4ifc.png')
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

# notification model
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.full_name} Date: ({self.date})"