from django.contrib import admin
from .models import StudentModel, StudentGradeModel

@admin.register(StudentModel)
class StudentModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'register_number', 'paid_amount']
    list_filter = ['groups']
    search_fields = ['user__first_name', 'user__last_name', 'register_number']
    list_per_page = 10

@admin.register(StudentGradeModel)
class StudentGradeModelAdmin(admin.ModelAdmin):
    list_display = ['student', 'group', 'grade']
    list_filter = ['group']
    search_fields = ['student__first_name', 'student__last_name', 'group__name']
    list_per_page = 10
