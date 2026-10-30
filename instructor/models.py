from django.db import models
from authentication.models import CRMUserModel
from course.models import CourseModel

class InstructorModel(models.Model):
    user = models.OneToOneField(CRMUserModel, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    courses = models.ManyToManyField(CourseModel, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

