from django.contrib import admin
from .models import DoctorStatistics, PatientStatistics, Notification

@admin.register(DoctorStatistics)
class DoctorStatisticsAdmin(admin.ModelAdmin):
    list_display = ('get_doctor_name', 'patients_verified', 'problems_resolved', 'last_updated')
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user_profile.user.first_name} {obj.doctor.user_profile.user.last_name}"
    get_doctor_name.short_description = 'Doctor'

@admin.register(PatientStatistics)
class PatientStatisticsAdmin(admin.ModelAdmin):
    list_display = ('get_patient_name', 'predictions_count', 'problems_submitted', 'last_updated')
    
    def get_patient_name(self, obj):
        return obj.patient.user_profile.user.username
    get_patient_name.short_description = 'Patient'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    
    def get_username(self, obj):
        return obj.user_profile.user.username
    get_username.short_description = 'User'
    search_fields = ('user_profile__user__username', 'title', 'message')
