from django.contrib import admin
from .models import UserProfile, Patient, Doctor

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'phone_number', 'created_at')
    list_filter = ('user_type', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'height', 'weight', 'blood_group')
    search_fields = ('user_profile__user__username', 'blood_group')
    
    def get_username(self, obj):
        return obj.user_profile.user.username
    get_username.short_description = 'Username'

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'specialization', 'experience_years', 'is_verified')
    list_filter = ('is_verified', 'specialization')
    search_fields = ('user_profile__user__username', 'specialization', 'license_number')
    
    def get_username(self, obj):
        return obj.user_profile.user.username
    get_username.short_description = 'Username'
