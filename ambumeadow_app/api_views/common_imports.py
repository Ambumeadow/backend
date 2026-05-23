# =========================
# Django Imports
# =========================
import json
import logging
import os
import secrets
import traceback
import uuid
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt

# =========================
# Django REST Framework
# =========================
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    parser_classes,
    permission_classes,
)
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

# =========================
# Firebase
# =========================
import firebase_admin
import pyrebase
from firebase_admin import auth, credentials

# =========================
# Third-Party Packages
# =========================
import requests
import resend

# =========================
# Local App Imports
# =========================
from ambumeadow_app.api_serializers.ambulance import (
    NearestAmbulanceSerializer,
)

from .helper import send_push_notification, send_email

from ambumeadow_app.models import (
    Ambulance,
    AmbulanceBooking,
    CareAppointment,
    Driver,
    DriverNotification,
    Hospital,
    MedicalRecord,
    Notification,
    Patient,
    Payment,
    Product,
    ProductOrder,
    Staff,
    StaffNotification,
    User,
    Chat,
)

from ambumeadow_app.serializers import NotificationSerializer

from ambumeadow_app.utils.distance import haversine
from ambumeadow_app.utils.verify_paystack import (
    verify_paystack_payment,
)

# =========================
# Logging
# =========================
logger = logging.getLogger("backend")