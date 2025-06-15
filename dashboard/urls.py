from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('patient/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dash/', views.admin_dashboard, name='admin_dash'),  # New URL for admin dashboard
    path('doctor/verify-prediction/<int:prediction_id>/', views.verify_prediction, name='verify_prediction'),
    path('doctor/respond-problem/<int:problem_id>/', views.respond_to_problem, name='respond_to_problem'),
    path('admin/verify-doctor/<int:doctor_id>/', views.verify_doctor, name='verify_doctor'),
    path('admin/manage-users/', views.manage_users, name='manage_users'),
    path('admin/prescriptions/', views.admin_prescriptions, name='admin_prescriptions'),  # New URL for prescriptions
    path('notifications/', views.notifications, name='notifications'),
    # Add this to your existing urlpatterns
    path('problem/assign/<int:problem_id>/', views.assign_problem, name='assign_problem'),
]