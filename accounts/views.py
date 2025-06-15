from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, Patient, Doctor
from django.db import transaction

def home(request):
    """Home page view"""
    return render(request, 'accounts/home.html')

def login_view(request):
    """Handle user login with different user types"""
    if request.user.is_authenticated:
        return redirect('dashboard_home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user has the correct user type
            try:
                user_profile = UserProfile.objects.get(user=user)
                
                # Debug information
                print(f"User type from form: {user_type}")
                print(f"User type in database: {user_profile.user_type}")
                
                # Check if user type matches or allow admin to login regardless of selected type
                if user_profile.user_type == user_type or user_profile.user_type == 'admin':
                    login(request, user)
                    
                    # Redirect based on actual user type (not the selected one)
                    if user_profile.user_type == 'patient':
                        return redirect('patient_dashboard')
                    elif user_profile.user_type == 'doctor':
                        return redirect('doctor_dashboard')
                    elif user_profile.user_type == 'admin':
                        return redirect('admin_dashboard')
                    else:
                        return redirect('home')
                else:
                    messages.error(request, f'This account is not registered as a {user_type}. Please select the correct user type.')
            except UserProfile.DoesNotExist:
                # Handle superuser without UserProfile
                if user.is_superuser and user_type == 'admin':
                    # Create a UserProfile for this superuser
                    UserProfile.objects.create(
                        user=user,
                        user_type='admin'
                    )
                    login(request, user)
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, 'User profile not found. Please contact administrator.')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('home')

def register(request):
    """Registration selection page"""
    return render(request, 'accounts/register.html')

@transaction.atomic
def register_patient(request):
    """Register a new patient"""
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        blood_group = request.POST.get('blood_group')
        
        # Validate passwords
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('register_patient')
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register_patient')
        
        # Check if email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register_patient')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create user profile
        profile_picture = request.FILES.get('profile_picture')
        user_profile = UserProfile.objects.create(
            user=user,
            user_type='patient',
            profile_picture=profile_picture,
            phone_number=phone_number,
            address=address,
            date_of_birth=date_of_birth
        )
        
        # Create patient
        patient = Patient.objects.create(
            user_profile=user_profile,
            blood_group=blood_group
            # Remove the gender field
        )
        
        messages.success(request, 'Registration successful. You can now login.')
        return redirect('login')
    
    return render(request, 'accounts/register_patient.html')

@transaction.atomic
def register_doctor(request):
    """Register a new doctor"""
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        date_of_birth = request.POST.get('date_of_birth')
        specialization = request.POST.get('specialization')
        qualification = request.POST.get('qualification')
        experience_years = request.POST.get('experience_years')
        license_number = request.POST.get('license_number')
        bio = request.POST.get('bio')
        consultation_fee = request.POST.get('consultation_fee')
        
        # Validate passwords
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('register_doctor')
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register_doctor')
        
        # Check if email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register_doctor')
        
        # Check if license number exists
        if Doctor.objects.filter(license_number=license_number).exists():
            messages.error(request, 'License number already exists')
            return redirect('register_doctor')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create user profile
        profile_picture = request.FILES.get('profile_picture')
        user_profile = UserProfile.objects.create(
            user=user,
            user_type='doctor',
            profile_picture=profile_picture,
            phone_number=phone_number,
            address=address,
            date_of_birth=date_of_birth
        )
        
        # Create doctor
        # Create doctor
        doctor = Doctor.objects.create(
            user_profile=user_profile,
            specialization=specialization,
            qualification=qualification,
            experience_years=experience_years,
            license_number=license_number,
            bio=bio,
            consultation_fee=consultation_fee if consultation_fee else 0  # Use default if not provided
        )
        
        messages.success(request, 'Registration successful. Please wait for admin verification before you can login.')
        return redirect('login')
    
    return render(request, 'accounts/register_doctor.html')

@transaction.atomic
def register_admin(request):
    """Register a new admin (should be restricted)"""
    # Check if the user is already an admin
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.user_type != 'admin':
                messages.error(request, 'You do not have permission to register an admin')
                return redirect('home')
        except UserProfile.DoesNotExist:
            messages.error(request, 'You do not have permission to register an admin')
            return redirect('home')
    else:
        # Check if there are any existing admins
        admin_count = UserProfile.objects.filter(user_type='admin').count()
        if admin_count > 0:
            messages.error(request, 'Admin registration is restricted')
            return redirect('home')
    
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        
        # Validate passwords
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('register_admin')
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register_admin')
        
        # Check if email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register_admin')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=True  # Give admin staff privileges
        )
        
        # Create user profile
        profile_picture = request.FILES.get('profile_picture')
        user_profile = UserProfile.objects.create(
            user=user,
            user_type='admin',
            profile_picture=profile_picture,
            phone_number=phone_number
        )
        
        messages.success(request, 'Admin registration successful. You can now login.')
        return redirect('login')
    
    return render(request, 'accounts/register_admin.html')

@login_required
def profile(request):
    """View user profile"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    context = {
        'user_profile': user_profile
    }
    
    # Add specific profile data based on user type
    if user_profile.user_type == 'patient':
        patient = Patient.objects.get(user_profile=user_profile)
        context['patient'] = patient
    elif user_profile.user_type == 'doctor':
        doctor = Doctor.objects.get(user_profile=user_profile)
        context['doctor'] = doctor
    
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile"""
    user_profile = UserProfile.objects.get(user=request.user)
    
    if request.method == 'POST':
        # Update user data
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        
        # Update user profile
        user_profile.phone_number = request.POST.get('phone_number')
        user_profile.address = request.POST.get('address')
        
        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']
        
        user_profile.save()
        
        # Update specific profile data based on user type
        if user_profile.user_type == 'patient':
            patient = Patient.objects.get(user_profile=user_profile)
            patient.gender = request.POST.get('gender')
            patient.blood_group = request.POST.get('blood_group')
            patient.save()
        elif user_profile.user_type == 'doctor':
            doctor = Doctor.objects.get(user_profile=user_profile)
            doctor.specialization = request.POST.get('specialization')
            doctor.qualification = request.POST.get('qualification')
            doctor.experience_years = request.POST.get('experience_years')
            doctor.bio = request.POST.get('bio')
            doctor.consultation_fee = request.POST.get('consultation_fee')
            doctor.save()
        
        messages.success(request, 'Profile updated successfully')
        return redirect('profile')
    
    context = {
        'user_profile': user_profile
    }
    
    # Add specific profile data based on user type
    if user_profile.user_type == 'patient':
        patient = Patient.objects.get(user_profile=user_profile)
        context['patient'] = patient
    elif user_profile.user_type == 'doctor':
        doctor = Doctor.objects.get(user_profile=user_profile)
        context['doctor'] = doctor
    
    return render(request, 'accounts/edit_profile.html', context)