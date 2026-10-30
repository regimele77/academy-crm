from django.contrib import admin
from .models import CourseModel, CourseGroupModel


@admin.register(CourseModel)
class CourseModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'instructor', 'price']
    list_filter = ['instructor']
    search_fields = ['name', 'instructor__user__first_name', 'instructor__user__last_name']
    list_per_page = 10

@admin.register(CourseGroupModel)
class CourseGroupModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'course', 'instructor']
    list_filter = ['course', 'instructor']
    search_fields = ['name', 'course__name', 'instructor__user__first_name', 'instructor__user__last_name']
    list_per_page = 10