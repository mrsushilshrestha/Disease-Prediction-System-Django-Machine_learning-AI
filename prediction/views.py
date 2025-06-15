from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Disease, Symptom, Prediction, PatientProblem
from accounts.models import Patient, Doctor, UserProfile
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from .symptom_mapping import map_user_symptom

def prediction_home(request):
    """Prediction home page"""
    symptoms = Symptom.objects.all().order_by('name')
    return render(request, 'prediction/prediction_home.html', {'symptoms': symptoms})

# Update the predict_disease function in views.py

from .ml_model import DiseasePredictor

# Initialize the predictor
predictor = DiseasePredictor()

def predict_disease(request):
    """Disease prediction view"""
    if request.method == 'POST':
        # Get selected symptoms from form
        selected_symptoms = request.POST.getlist('symptoms')
        
        # Map user symptoms to training data symptoms
        mapped_symptoms = [map_user_symptom(symptom) for symptom in selected_symptoms]
        
        # Predict disease using the model
        predictor = DiseasePredictor()
        disease_name, confidence = predictor.predict(mapped_symptoms)
        
        # Get or create disease object
        disease, created = Disease.objects.get_or_create(name=disease_name)
        
        # Create prediction record
        prediction = Prediction.objects.create(
            patient=request.user.patient if hasattr(request.user, 'patient') else None,
            symptoms=', '.join(selected_symptoms),
            predicted_disease=disease,
            confidence_score=confidence
        )
        
        return render(request, 'prediction/prediction_result.html', {
            'prediction': prediction,
            'disease': disease
        })
    else:
        # Get all symptoms for the form
        symptoms = Symptom.objects.all().order_by('name')
        return render(request, 'prediction/predict.html', {'symptoms': symptoms})
    if not selected_symptoms:
        messages.error(request, 'Please select at least one symptom')
        return redirect('prediction_home')
    
    # Convert symptoms to string for storage
    symptoms_str = ','.join(selected_symptoms)
    
    # Perform prediction using our ML model
    disease_name, confidence_score = predictor.predict(selected_symptoms)
    
    # Get or create the disease
    disease, created = Disease.objects.get_or_create(
        name=disease_name,
        defaults={
            'description': f'Information about {disease_name}',
            'symptoms': symptoms_str,
            'causes': f'Common causes of {disease_name}',
            'home_remedies': f'Home remedies for {disease_name}',
            'medications': f'Common medications for {disease_name}'
        }
    )
    
    # Create prediction record
    prediction = Prediction(
        symptoms=symptoms_str,
        predicted_disease=disease,
        confidence_score=confidence_score,
        is_verified=False
    )
    
    # Associate with patient if user is logged in
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.user_type == 'patient':
                patient = Patient.objects.get(user_profile=user_profile)
                prediction.patient = patient
        except (UserProfile.DoesNotExist, Patient.DoesNotExist):
            pass
    
    prediction.save()
    
    return redirect('prediction_result', prediction_id=prediction.id)

def prediction_result(request, prediction_id):
    """Display prediction result"""
    prediction = get_object_or_404(Prediction, id=prediction_id)
    
    # Parse symptoms string back to list
    symptoms_list = prediction.symptoms.split(',')
    
    context = {
        'prediction': prediction,
        'symptoms_list': symptoms_list,
    }
    
    return render(request, 'prediction/prediction_result.html', context)

@login_required
def prediction_history(request):
    """View prediction history for logged-in patients"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    if user_profile.user_type != 'patient':
        messages.error(request, 'Only patients can view prediction history')
        return redirect('home')
    
    patient = Patient.objects.get(user_profile=user_profile)
    predictions = Prediction.objects.filter(patient=patient).order_by('-created_at')
    
    return render(request, 'prediction/prediction_history.html', {'predictions': predictions})

@login_required
def submit_problem(request):
    """Submit a health problem"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    if user_profile.user_type != 'patient':
        messages.error(request, 'Only patients can submit problems')
        return redirect('home')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        symptoms = request.POST.get('symptoms')
        duration = request.POST.get('duration')
        taking_medicine = request.POST.get('taking_medicine')
        medicine_details = request.POST.get('medicine_details') if taking_medicine == 'yes' else None
        
        patient = Patient.objects.get(user_profile=user_profile)
        
        problem = PatientProblem.objects.create(
            patient=patient,
            title=title,
            description=description,
            symptoms=symptoms,
            duration=duration,
            taking_medicine=taking_medicine,
            medicine_details=medicine_details,
            status='pending'
        )
        
        # Handle picture upload if present
        if 'picture' in request.FILES:
            problem.picture = request.FILES['picture']
            problem.save()
        
        messages.success(request, 'Your problem has been submitted successfully')
        return redirect('problem_detail', problem_id=problem.id)
    
    return render(request, 'prediction/submit_problem.html')

@login_required
def problem_detail(request, problem_id):
    """View problem details"""
    problem = get_object_or_404(PatientProblem, id=problem_id)
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Check if user is the patient who submitted the problem or a doctor
    if user_profile.user_type == 'patient':
        patient = Patient.objects.get(user_profile=user_profile)
        if problem.patient != patient:
            messages.error(request, 'You do not have permission to view this problem')
            return redirect('home')
    elif user_profile.user_type != 'doctor' and user_profile.user_type != 'admin':
        messages.error(request, 'You do not have permission to view this problem')
        return redirect('home')
    
    return render(request, 'prediction/problem_detail.html', {'problem': problem})

@login_required
def problem_list(request):
    """List all problems for the logged-in patient"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    if user_profile.user_type != 'patient':
        messages.error(request, 'Only patients can view their problems')
        return redirect('home')
    
    patient = Patient.objects.get(user_profile=user_profile)
    problems = PatientProblem.objects.filter(patient=patient).order_by('-created_at')
    
    return render(request, 'prediction/problem_list.html', {'problems': problems})


def unassigned_problems(request):
    """View all unassigned problems (doctors only)"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    if user_profile.user_type != 'doctor':
        messages.error(request, 'Only doctors can view unassigned problems')
        return redirect('home')
    
    doctor = Doctor.objects.get(user_profile=user_profile)
    
    if not doctor.is_verified:
        messages.error(request, 'You need to be verified to view unassigned problems')
        return redirect('doctor_dashboard')
    
    # Get all unassigned problems
    problems = PatientProblem.objects.filter(assigned_doctor=None, status='pending').order_by('-created_at')
    
    return render(request, 'prediction/unassigned_problems.html', {'problems': problems})
