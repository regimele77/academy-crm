from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/profile/', views.student_profile, name='student_profile'),
]