from django.urls import path
from . import views

urlpatterns = [
    path('', views.prediction_home, name='prediction_home'),
    path('predict/', views.predict_disease, name='predict_disease'),
    path('result/<int:prediction_id>/', views.prediction_result, name='prediction_result'),
    path('history/', views.prediction_history, name='prediction_history'),
    path('problem/submit/', views.submit_problem, name='submit_problem'),
    path('problem/<int:problem_id>/', views.problem_detail, name='problem_detail'),
    path('problem/list/', views.problem_list, name='problem_list'),
    # Add this to the existing urlpatterns list
    path('problem/unassigned/', views.unassigned_problems, name='unassigned_problems'),
]