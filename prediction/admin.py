from django.contrib import admin
from .models import Disease, Symptom, Prediction, PatientProblem

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'symptoms')

@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('get_patient_username', 'predicted_disease', 'confidence_score', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('patient__user_profile__user__username', 'predicted_disease__name')
    
    def get_patient_username(self, obj):
        if obj.patient:
            return obj.patient.user_profile.user.username
        return 'Anonymous'
    get_patient_username.short_description = 'Patient'

@admin.register(PatientProblem)
class PatientProblemAdmin(admin.ModelAdmin):
    list_display = ('get_patient_username', 'title', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('patient__user_profile__user__username', 'title', 'description')
    
    def get_patient_username(self, obj):
        return obj.patient.user_profile.user.username
    get_patient_username.short_description = 'Patient'
