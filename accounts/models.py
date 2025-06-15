from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_TYPES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='patient')
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.user_type}"

class Patient(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='patient_profile')
    gender = models.CharField(max_length=10, blank=True, null=True)  # Add this line
    height = models.FloatField(help_text="Height in cm", blank=True, null=True)
    weight = models.FloatField(help_text="Weight in kg", blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    blood_pressure = models.CharField(max_length=20, blank=True, null=True)
    sugar_level = models.CharField(max_length=20, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Patient: {self.user_profile.user.username}"

class Doctor(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    experience_years = models.PositiveIntegerField(default=0)
    license_number = models.CharField(max_length=50, unique=True)
    is_verified = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Dr. {self.user_profile.user.first_name} {self.user_profile.user.last_name} - {self.specialization}"
