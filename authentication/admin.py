from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CRMUserModel

@admin.register(CRMUserModel)
class CRMUserModelAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'phone', 'created_at', 'updated_at']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    list_filter = ['created_at', 'updated_at']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
