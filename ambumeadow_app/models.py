from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager

# -----------------------------
# 1. User Model
# -----------------------------
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.CharField(max_length=100, default="johndoe@example.com")
    username = models.CharField(max_length=150, unique=True)
    agreed = models.BooleanField(default=False)
    current_lat = models.FloatField(null=True, blank=True, default=0.0)
    current_lng = models.FloatField(null=True, blank=True, default=0.0)
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, null=True, blank=True)
    reset_token = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    profile_image = models.URLField(default="https://res.cloudinary.com/dc68huvjj/image/upload/v1748102584/kwwwa0avlfoeybpi3key.png")
    date_joined = models.DateTimeField(default=timezone.now)
    expo_token = models.CharField(max_length=100, default="hsvsx92jjs", null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return f"#{self.id} {self.full_name} Date joined: {self.date_joined} {self.is_active}"

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
    id_number = models.CharField(max_length=8, default='12345678')
    firebase_uid = models.CharField(max_length=256, default="@Ambumeadow2025")
    phone_verified = models.BooleanField(default=False)
    agreed = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)
    profile_image = models.URLField(default="https://res.cloudinary.com/dc68huvjj/image/upload/v1748102584/kwwwa0avlfoeybpi3key.png")
    expo_token = models.CharField(max_length=100, default="hsvsx92jjs")
    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.full_name} Date joined: ({self.date_joined})"

# staff model
class Staff(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
    ]

    STATUS = [
        ('active', 'Active'),
        ('busy', 'Busy'),
        ('inactive', 'Inactive'),
    ]

    DEPARTMENT = [
        ('cardiology', 'Cardiology'),
        ('neurology', 'Neurology'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')

    hospital = models.ForeignKey(Hospital,on_delete=models.CASCADE,null=True,blank=True)

    id_number = models.CharField(max_length=20)

    medical_license_number = models.CharField(max_length=50,unique=True,null=True,blank=True)

    department = models.CharField(max_length=100,choices=DEPARTMENT,default='other')

    role = models.CharField(max_length=20,choices=ROLE_CHOICES,default='other')

    status = models.CharField(max_length=20,choices=STATUS,default='active')

    date_joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.full_name} - {self.role}"

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

# driver notification model
class DriverNotification(models.Model):
    TYPES = [
        ('emergency','Emergency'),
        ('update','Update'),
        ('system', 'System'),
    ]
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    message = models.TextField()
    message_type = models.CharField(max_length=20, choices=TYPES, default='update')
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.driver.full_name} {self.message_type} Date: ({self.date})"

# ambulance model
class Ambulance(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('maintenance', 'Maintenance'),
        ('out_of_service', 'Out of Service'),
    ]
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    plate_number = models.CharField(max_length=20, unique=True)
    is_available = models.BooleanField(default=True)
    current_lat = models.FloatField(null=True, blank=True, default=0.0)
    current_lng = models.FloatField(null=True, blank=True, default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
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
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, default=1)
    product_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    image = models.URLField(default="https://res.cloudinary.com/dc68huvjj/image/upload/v1748102584/kwwwa0avlfoeybpi3key.png")
    requires_prescription = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    expiry_date = models.DateField(null=True, blank=True, default=timezone.now)
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
    latitude = models.FloatField(null=True, blank=True, default=0.0)
    longitude = models.FloatField(null=True, blank=True, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user_id.full_name} for {self.product_id.product_name}"

# payment model
class Payment(models.Model):
    METHOD_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('card', 'Card'),
        ('wallet', 'Wallet'),
        ('paystack', 'Paystack')
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    SERVICES_CHOICES = [
        ('merchandise', 'Merchandise'),
        ('care_appointment', 'Care Appointment'),
        ('ambulance_booking', 'Ambulance Booking'),
        ('other', "Other"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=100, choices=SERVICES_CHOICES, default='other' )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    receipt_number = models.CharField(max_length=100, default="")
    checkout_request_id = models.CharField(max_length=100, default="")
    merchant_request_id = models.CharField(max_length=100, default="")
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"#{self.id} {self.user.full_name} - {self.service_type} - {self.amount}"

# ambulance booking
class AmbulanceBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ambulance = models.ForeignKey(Ambulance, on_delete=models.CASCADE)
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    booking_datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Ambulance {self.ambulance.plate_number} booked by {self.user.full_name}"

# care appointment model
class CareAppointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True)
    care_type = models.CharField(max_length=100)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    home_address = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.full_name} - {self.care_type}"

# chat model for doctor-patient communication
class Chat(models.Model):
    SENDER_TYPES = [
        ("patient", "Patient"),
        ("doctor", "Doctor"),
    ]
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="doctor_chats")
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="patient_chats")
    message = models.TextField()
    sender_type = models.CharField(max_length=10, choices=SENDER_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.sender_type}: {self.message[:30]}"

# package model for subscription plans
class Package(models.Model):
    NAMES = [
        ("family", "Family"),
        ("individual", "Individual"),
    ]
    CATEGORIES = [
        ("bronze", "Bronze"),
        ("silver", "Silver"),
        ("gold", "Gold"),
        ("platinum", "Platinum"),
    ]
    name = models.CharField(max_length=100, choices=NAMES, default="Individual")
    category = models.CharField(max_length=100, choices=CATEGORIES, default="Bronze")
    maximum_members = models.IntegerField()
    no_of_consultations = models.IntegerField()
    access_telemedicine = models.BooleanField(default=False)
    book_ambulance = models.BooleanField(default=False)
    book_care_appointment = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} {self.price}"

# subscription model for users subscribing to packages
class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.full_name} subscribed to {self.package.name}"
