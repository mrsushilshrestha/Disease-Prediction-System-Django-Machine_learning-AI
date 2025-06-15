from django.db import models
from accounts.models import Doctor, Patient

class DoctorStatistics(models.Model):
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE, related_name='statistics')
    patients_verified = models.PositiveIntegerField(default=0)
    problems_resolved = models.PositiveIntegerField(default=0)
    average_response_time = models.FloatField(default=0)  # in hours
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Statistics for Dr. {self.doctor.user_profile.user.first_name} {self.doctor.user_profile.user.last_name}"

class PatientStatistics(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='statistics')
    predictions_count = models.PositiveIntegerField(default=0)
    problems_submitted = models.PositiveIntegerField(default=0)
    last_prediction_date = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Statistics for {self.patient.user_profile.user.username}"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('prediction', 'Prediction Result'),
        ('verification', 'Doctor Verification'),
        ('problem', 'Problem Response'),
        ('system', 'System Notification'),
    )
    
    user_profile = models.ForeignKey('accounts.UserProfile', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user_profile.user.username} - {self.title}"
