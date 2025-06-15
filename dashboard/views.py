from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from accounts.models import UserProfile, Patient, Doctor
from prediction.models import Prediction, PatientProblem, Disease
from .models import DoctorStatistics, PatientStatistics, Notification
from django.db.models import Count, Avg

@login_required
def dashboard_home(request):
    """Redirect to appropriate dashboard based on user type"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    if user_profile.user_type == 'patient':
        return redirect('patient_dashboard')
    elif user_profile.user_type == 'doctor':
        return redirect('doctor_dashboard')
    elif user_profile.user_type == 'admin':
        return redirect('admin_dashboard')
    else:
        return redirect('home')

@login_required
def patient_dashboard(request):
    """Dashboard for patients"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    if user_profile.user_type != 'patient':
        messages.error(request, 'You do not have permission to access this dashboard')
        return redirect('home')
    
    # Try to get the patient or create a new one if it doesn't exist
    patient, created = Patient.objects.get_or_create(user_profile=user_profile)
    
    if created:
        messages.info(request, 'Your patient profile was incomplete. Please update your profile.')
    
    # Get recent predictions
    recent_predictions = Prediction.objects.filter(patient=patient).order_by('-created_at')[:5]
    
    # Get recent problems
    recent_problems = PatientProblem.objects.filter(patient=patient).order_by('-created_at')[:5]
    
    # Get unread notifications
    notifications = Notification.objects.filter(user_profile=user_profile, is_read=False).order_by('-created_at')[:5]
    
    # Get or create patient statistics
    stats, created = PatientStatistics.objects.get_or_create(patient=patient)
    
    # Update statistics if needed
    predictions_count = Prediction.objects.filter(patient=patient).count()
    problems_submitted = PatientProblem.objects.filter(patient=patient).count()
    
    if stats.predictions_count != predictions_count or stats.problems_submitted != problems_submitted:
        stats.predictions_count = predictions_count
        stats.problems_submitted = problems_submitted
        stats.save()
    
    context = {
        'patient': patient,
        'recent_predictions': recent_predictions,
        'recent_problems': recent_problems,
        'notifications': notifications,
        'stats': stats
    }
    
    return render(request, 'dashboard/patient_dashboard.html', context)

@login_required
def doctor_dashboard(request):
    """Dashboard for doctors"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    if user_profile.user_type != 'doctor':
        messages.error(request, 'You do not have permission to access this dashboard')
        return redirect('home')
    
    doctor = Doctor.objects.get(user_profile=user_profile)
    
    # Check if doctor is verified
    if not doctor.is_verified:
        return render(request, 'dashboard/doctor_verification_pending.html')
    
    # Get pending predictions to verify
    pending_predictions = Prediction.objects.filter(is_verified=False).order_by('-created_at')[:10]
    
    # Get assigned problems
    assigned_problems = PatientProblem.objects.filter(assigned_doctor=doctor).order_by('-created_at')
    
    # Apply filter if provided
    problem_filter = request.GET.get('problem_filter', 'all')
    if problem_filter != 'all' and problem_filter in ['pending', 'in_review', 'resolved']:
        assigned_problems = assigned_problems.filter(status=problem_filter)
    
    # Check if this is an AJAX request
    if request.GET.get('ajax') == 'true':
        from django.http import JsonResponse
        
        # Prepare problems data for JSON response
        problems_data = []
        for problem in assigned_problems:
            problems_data.append({
                'id': problem.id,
                'created_at': problem.created_at.isoformat(),
                'patient_name': problem.patient.user_profile.user.username,
                'title': problem.title,
                'status': problem.status,
            })
        
        return JsonResponse({'problems': problems_data})
    
    # Get unread notifications
    notifications = Notification.objects.filter(user_profile=user_profile, is_read=False).order_by('-created_at')[:5]
    
    # Get or create doctor statistics
    stats, created = DoctorStatistics.objects.get_or_create(doctor=doctor)
    
    # Update statistics if needed
    patients_verified = Prediction.objects.filter(verified_by=doctor).count()
    problems_resolved = PatientProblem.objects.filter(assigned_doctor=doctor, status='resolved').count()
    
    if stats.patients_verified != patients_verified or stats.problems_resolved != problems_resolved:
        stats.patients_verified = patients_verified
        stats.problems_resolved = problems_resolved
        stats.save()
    
    context = {
        'doctor': doctor,
        'pending_predictions': pending_predictions,
        'assigned_problems': assigned_problems,
        'notifications': notifications,
        'stats': stats,
        'problem_filter': problem_filter  # Pass the current filter to the template
    }
    
    return render(request, 'dashboard/doctor_dashboard.html', context)

@login_required
def admin_dashboard(request):
    """Dashboard for admin"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    if user_profile.user_type != 'admin':
        messages.error(request, 'You do not have permission to access this dashboard')
        return redirect('home')
    
    # Get pending doctor verifications
    pending_doctors = Doctor.objects.filter(is_verified=False)
    
    # Get system statistics
    total_users = User.objects.count()
    total_patients = Patient.objects.count()
    total_doctors = Doctor.objects.count()
    total_predictions = Prediction.objects.count()
    total_problems = PatientProblem.objects.count()
    
    # Get disease statistics
    disease_stats = Prediction.objects.values('predicted_disease__name').annotate(count=Count('id')).order_by('-count')[:5]
    
    context = {
        'pending_doctors': pending_doctors,
        'total_users': total_users,
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_predictions': total_predictions,
        'total_problems': total_problems,
        'disease_stats': disease_stats
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def verify_prediction(request, prediction_id):
    """Verify a disease prediction"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    if user_profile.user_type != 'doctor':
        messages.error(request, 'Only doctors can verify predictions')
        return redirect('home')
    
    doctor = Doctor.objects.get(user_profile=user_profile)
    
    if not doctor.is_verified:
        messages.error(request, 'You need to be verified to perform this action')
        return redirect('doctor_dashboard')
    
    prediction = get_object_or_404(Prediction, id=prediction_id)
    
    if request.method == 'POST':
        # Update prediction verification
        prediction.is_verified = True
        prediction.verified_by = doctor
        prediction.doctor_notes = request.POST.get('doctor_notes')
        prediction.save()
        
        # Update doctor statistics
        stats, created = DoctorStatistics.objects.get_or_create(doctor=doctor)
        stats.patients_verified += 1
        stats.save()
        
        # Create notification for patient if prediction is associated with a patient
        if prediction.patient:
            patient_profile = prediction.patient.user_profile
            Notification.objects.create(
                user_profile=patient_profile,
                title='Prediction Verified',
                message=f'Your prediction for {prediction.predicted_disease.name} has been verified by Dr. {doctor.user_profile.user.first_name} {doctor.user_profile.user.last_name}.',
                notification_type='verification'
            )
        
        messages.success(request, 'Prediction verified successfully')
        return redirect('doctor_dashboard')
    
    return render(request, 'dashboard/verify_prediction.html', {'prediction': prediction})

@login_required
def respond_to_problem(request, problem_id):
    """Respond to a patient problem"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    if user_profile.user_type != 'doctor':
        messages.error(request, 'Only doctors can respond to problems')
        return redirect('home')
    
    doctor = Doctor.objects.get(user_profile=user_profile)
    
    if not doctor.is_verified:
        messages.error(request, 'You need to be verified to perform this action')
        return redirect('doctor_dashboard')
    
    problem = get_object_or_404(PatientProblem, id=problem_id)
    
    if request.method == 'POST':
        # Update problem with doctor's response
        problem.doctor_response = request.POST.get('doctor_response')
        problem.status = 'resolved'
        problem.assigned_doctor = doctor
        problem.save()
        
        # Update doctor statistics
        stats, created = DoctorStatistics.objects.get_or_create(doctor=doctor)
        stats.problems_resolved += 1
        stats.save()
        
        # Create notification for patient
        Notification.objects.create(
            user_profile=problem.patient.user_profile,
            title='Problem Response',
            message=f'Your problem "{problem.title}" has been addressed by Dr. {doctor.user_profile.user.first_name} {doctor.user_profile.user.last_name}.',
            notification_type='problem'
        )
        
        messages.success(request, 'Response submitted successfully')
        return redirect('doctor_dashboard')
    
    return render(request, 'dashboard/respond_to_problem.html', {'problem': problem})

@login_required
def verify_doctor(request, doctor_id):
    """Verify a doctor account"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    if user_profile.user_type != 'admin':
        messages.error(request, 'Only admins can verify doctors')
        return redirect('home')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'verify':
            doctor.is_verified = True
            doctor.save()
            
            # Create notification for doctor
            Notification.objects.create(
                user_profile=doctor.user_profile,
                title='Account Verified',
                message='Your doctor account has been verified. You can now access all doctor features.',
                notification_type='system'
            )
            
            messages.success(request, 'Doctor verified successfully')
        elif action == 'reject':
            # Optionally, you could delete the doctor account or mark it as rejected
            doctor.is_verified = False
            doctor.save()
            
            # Create notification for doctor
            Notification.objects.create(
                user_profile=doctor.user_profile,
                title='Account Verification Failed',
                message='Your doctor account verification was not approved. Please contact the administrator for more information.',
                notification_type='system'
            )
            
            messages.success(request, 'Doctor rejected successfully')
        
        return redirect('admin_dashboard')
    
    return render(request, 'dashboard/verify_doctor.html', {'doctor': doctor})

@login_required
def manage_users(request):
    """Manage users (admin only)"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    if user_profile.user_type != 'admin':
        messages.error(request, 'Only admins can manage users')
        return redirect('home')
    
    # Handle filter parameter
    filter_param = request.GET.get('filter', 'all')
    
    # Get all users with their profiles
    user_profiles = UserProfile.objects.all().select_related('user')
    
    # Apply filters
    if filter_param == 'patient':
        user_profiles = user_profiles.filter(user_type='patient')
    elif filter_param == 'doctor':
        user_profiles = user_profiles.filter(user_type='doctor')
    elif filter_param == 'admin':
        user_profiles = user_profiles.filter(user_type='admin')
    elif filter_param == 'active':
        user_profiles = user_profiles.filter(user__is_active=True)
    elif filter_param == 'inactive':
        user_profiles = user_profiles.filter(user__is_active=False)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        
        if action and user_id:
            target_user = get_object_or_404(User, id=user_id)
            target_profile = UserProfile.objects.get(user=target_user)
            
            # Don't allow admins to deactivate themselves
            if target_user == request.user and action in ['deactivate', 'delete']:
                messages.error(request, 'You cannot deactivate or delete your own account')
                return redirect('manage_users')
            
            if action == 'deactivate':
                target_user.is_active = False
                target_user.save()
                messages.success(request, f'User {target_user.username} deactivated successfully')
            elif action == 'activate':
                target_user.is_active = True
                target_user.save()
                messages.success(request, f'User {target_user.username} activated successfully')
            elif action == 'delete':
                # This will cascade delete the profile and related objects
                target_user.delete()
                messages.success(request, f'User deleted successfully')
        
        return redirect('manage_users')
    
    return render(request, 'dashboard/manage_users.html', {'user_profiles': user_profiles, 'current_filter': filter_param})

@login_required
def notifications(request):
    """View and manage notifications"""
    user_profile = UserProfile.objects.get(user=request.user)
    notifications = Notification.objects.filter(user_profile=user_profile).order_by('-created_at')
    
    # Mark all as read if requested
    if request.method == 'POST' and 'mark_all_read' in request.POST:
        notifications.update(is_read=True)
        messages.success(request, 'All notifications marked as read')
        return redirect('notifications')
    
    return render(request, 'dashboard/notifications.html', {'notifications': notifications})

@login_required
def assign_problem(request, problem_id):
    """Assign a problem to the logged-in doctor"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    if user_profile.user_type != 'doctor':
        messages.error(request, 'Only doctors can take cases')
        return redirect('home')
    
    doctor = Doctor.objects.get(user_profile=user_profile)
    
    if not doctor.is_verified:
        messages.error(request, 'You need to be verified to take cases')
        return redirect('doctor_dashboard')
    
    problem = get_object_or_404(PatientProblem, id=problem_id)
    
    # Check if problem is already assigned
    if problem.assigned_doctor:
        messages.error(request, 'This problem is already assigned to a doctor')
        return redirect('problem_detail', problem_id=problem.id)
    
    # Assign the problem to this doctor
    problem.assigned_doctor = doctor
    problem.status = 'in_review'
    problem.save()
    
    # Create notification for patient
    Notification.objects.create(
        user_profile=problem.patient.user_profile,
        title='Problem Assigned',
        message=f'Your problem "{problem.title}" has been taken by Dr. {doctor.user_profile.user.first_name} {doctor.user_profile.user.last_name}.',
        notification_type='problem'
    )
    
    messages.success(request, 'You have successfully taken this case')
    return redirect('problem_detail', problem_id=problem.id)

@login_required
def admin_prescriptions(request):
    """View all prescriptions (admin only)"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    if user_profile.user_type != 'admin':
        messages.error(request, 'Only admins can view all prescriptions')
        return redirect('home')
    
    # Handle filter parameter
    filter_param = request.GET.get('filter', 'all')
    
    # Get all predictions
    predictions = Prediction.objects.all().select_related(
        'patient__user_profile__user',
        'predicted_disease',
        'verified_by__user_profile__user'
    ).order_by('-created_at')
    
    # Apply filters
    if filter_param == 'verified':
        predictions = predictions.filter(is_verified=True)
    elif filter_param == 'unverified':
        predictions = predictions.filter(is_verified=False)
    
    return render(request, 'dashboard/admin_prescriptions.html', {
        'predictions': predictions,
        'current_filter': filter_param
    })
