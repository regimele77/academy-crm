from decimal import Decimal

from django.contrib import messages
from django.db.models import Avg, Prefetch
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from authentication.forms import ContactProfileForm
from course.models import CourseGroupModel

from .decorators import student_required
from .models import StudentGradeModel, StudentModel


@student_required
def student_dashboard(request):
    # Always scoped to the authenticated student's own profile (set by decorator).
    student = (
        StudentModel.objects
        .select_related('user')
        .prefetch_related(
            Prefetch(
                'groups',
                queryset=CourseGroupModel.objects.select_related(
                    'course',
                    'instructor__user',
                ).order_by('start_date'),
            ),
        )
        .get(pk=request.student.pk, user=request.user)
    )

    grades = (
        StudentGradeModel.objects
        .filter(student=request.user)
        .select_related('group', 'group__course')
        .order_by('-updated_at', '-created_at')
    )
    recent_grades = list(grades[:6])

    average_grade = grades.aggregate(average=Avg('grade'))['average']
    grade_count = grades.count()

    groups = list(student.groups.all())
    course_total = sum((group.course.price for group in groups), Decimal('0.00'))
    balance_due = course_total - student.paid_amount

    context = {
        'student': student,
        'groups': groups,
        'recent_grades': recent_grades,
        'grade_count': grade_count,
        'average_grade': average_grade,
        'course_total': course_total,
        'balance_due': balance_due,
        'active_nav': 'dashboard',
    }
    return render(request, 'student_dashboard.html', context)


@student_required
@require_http_methods(['GET', 'POST'])
def student_profile(request):
    student = (
        StudentModel.objects
        .select_related('user')
        .prefetch_related(
            Prefetch(
                'groups',
                queryset=CourseGroupModel.objects.select_related(
                    'course',
                    'instructor__user',
                ).order_by('start_date'),
            ),
        )
        .get(pk=request.student.pk, user=request.user)
    )

    if request.method == 'POST':
        form = ContactProfileForm(request.POST, request.FILES, instance=student.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your contact details were updated.')
            return redirect('student_profile')
    else:
        form = ContactProfileForm(instance=student.user)

    grades = StudentGradeModel.objects.filter(student=request.user)
    average_grade = grades.aggregate(average=Avg('grade'))['average']
    grade_count = grades.count()

    groups = list(student.groups.all())
    course_total = sum((group.course.price for group in groups), Decimal('0.00'))
    balance_due = course_total - student.paid_amount

    context = {
        'student': student,
        'form': form,
        'groups': groups,
        'grade_count': grade_count,
        'average_grade': average_grade,
        'course_total': course_total,
        'balance_due': balance_due,
        'active_nav': 'profile',
    }
    return render(request, 'student_profile.html', context)
