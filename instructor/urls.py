from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('dashboard/courses/', views.instructor_courses, name='instructor_courses'),
    path('dashboard/courses/create/', views.instructor_create_course, name='instructor_create_course'),
    path('dashboard/courses/edit/<int:course_id>/', views.instructor_edit_course, name='instructor_edit_course'),
    path(
        'dashboard/courses/<int:course_id>/groups/create/',
        views.instructor_create_course_group,
        name='instructor_create_course_group',
    ),
    path('dashboard/courses/delete/<int:course_id>/', views.instructor_delete_course, name='instructor_delete_course'),
    path('dashboard/groups/', views.instructor_groups, name='instructor_groups'),
    path('dashboard/groups/create/', views.instructor_create_group, name='instructor_create_group'),
    path('dashboard/groups/edit/<int:group_id>/', views.instructor_edit_group, name='instructor_edit_group'),
    path('dashboard/groups/delete/<int:group_id>/', views.instructor_delete_group, name='instructor_delete_group'),
    path(
        'dashboard/groups/<int:group_id>/students/add/',
        views.instructor_add_group_student,
        name='instructor_add_group_student',
    ),
    path('dashboard/profile/', views.instructor_profile, name='instructor_profile'),
]