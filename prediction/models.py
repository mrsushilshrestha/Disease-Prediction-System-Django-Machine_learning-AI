from django.db import models
from accounts.models import Patient, Doctor

class Disease(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    symptoms = models.TextField(help_text="Comma separated list of symptoms")
    causes = models.TextField()
    home_remedies = models.TextField(blank=True, null=True)
    medications = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Symptom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Prediction(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='predictions', null=True, blank=True)
    symptoms = models.TextField()
    predicted_disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='predictions')
    confidence_score = models.FloatField()
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_predictions')
    doctor_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        patient_info = self.patient.user_profile.user.username if self.patient else "Anonymous"
        return f"{patient_info} - {self.predicted_disease.name} ({self.confidence_score:.2f})"

class PatientProblem(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_review', 'In Review'),
        ('resolved', 'Resolved'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='problems')
    title = models.CharField(max_length=200)
    description = models.TextField()
    # Add these new fields
    symptoms = models.TextField(blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True)
    taking_medicine = models.CharField(max_length=5, blank=True, null=True)
    medicine_details = models.TextField(blank=True, null=True)
    picture = models.ImageField(upload_to='problem_images/', blank=True, null=True)
    # Existing fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_problems')
    doctor_response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient.user_profile.user.username} - {self.title}"
