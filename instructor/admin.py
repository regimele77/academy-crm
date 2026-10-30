from django.contrib import admin
from .models import InstructorModel

@admin.register(InstructorModel)
class InstructorModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'description', 'salary']
    list_filter = ['courses']
    search_fields = ['user__first_name', 'user__last_name', 'description']
    list_per_page = 10


