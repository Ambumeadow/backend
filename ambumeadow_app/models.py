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

    def __str__(self):
        return f"{self.hospital_name} Date joined: ({self.date_joined})"

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
    STATUS = [
        ('active', 'Active'),
        ('busy', 'Busy'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]
    DEPARTMENT = [
        ('cardiology', 'Cardiology'),
        ('neurology', 'Neurology'),
        ('orthopedics', 'Orthopedics'),
        ('pediatrics', 'Pediatrics'),
        ('emergency', 'Emergency'),
        ('radiology', 'Radiology'),
        ('general_medicine', 'General Medicine'),
        ('surgery', 'Surgery'),
        ('other', 'Other'),
    ]
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.CharField(max_length=100, default="johndoe@example.com")
    id_number = models.CharField(max_length=8, default='12345678')
    medical_license_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, choices=DEPARTMENT, default='other')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='other')
    status = models.CharField(max_length=20, choices=STATUS, default='active')
    firebase_uid = models.CharField(max_length=256, default="@Ambumeadow2025")
    phone_verified = models.BooleanField(default=False)
    agreed = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    profile_image = models.URLField(blank=True, null=True, default='')
    expo_token = models.CharField(max_length=100, default="hsvsx92jjs")
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.id} - {self.full_name} Date joined: ({self.date_joined})"

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
    is_available = models.BooleanField(default=True)
    current_lat = models.FloatField(null=True, blank=True, default=0.0)
    current_lng = models.FloatField(null=True, blank=True, default=0.0)
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Ambulance {self.plate_number} Driver: {self.driver.full_name}"

# product model - for the merchandise store
class Product(models.Model):
    CATEGORY_CHOICES = [
        ("emergency", "Emergency"),
        ("antibiotic", "Antibiotics"),
        ("pain_relief", "Pain Relief"),
        ("chronic", "Chronic Care"),
        ("pediatric", "Child & Maternal"),
        ("digestive", "Digestive"),
        ("respiratory", "Respiratory"),
        ("mental_health", "Mental Health"),
        ("skin", "Skin Care"),
        ("supplements", "Supplements"),
    ]
    
    product_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    requires_prescription = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.product_name} {self.price} {self.quantity}"

# model for product orders
class ProductOrder(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_orders', default=1)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user_id.full_name} for {self.product_id.product_name}"

# care appointment model
class CareAppointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Staff, on_delete=models.CASCADE)
    care_type = models.CharField(max_length=100)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='scheduled')
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.full_name} - {self.care_type}"
