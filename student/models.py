from django.db import models
from course.models import CourseGroupModel

class StudentModel(models.Model):
    user = models.OneToOneField('authentication.CRMUserModel', on_delete=models.CASCADE)
    register_number = models.CharField(max_length=255)
    groups = models.ManyToManyField(CourseGroupModel, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class StudentGradeModel(models.Model):
    student = models.ForeignKey('authentication.CRMUserModel', on_delete=models.CASCADE)
    group = models.ForeignKey(CourseGroupModel, on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.student.first_name} {self.student.last_name} - {self.group.name} - {self.grade}'

