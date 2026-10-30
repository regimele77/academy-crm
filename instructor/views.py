from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.db.models import Count, Prefetch, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from authentication.forms import ContactProfileForm
from course.models import CourseGroupModel, CourseModel
from student.models import StudentGradeModel, StudentModel

from .decorators import instructor_required
from .forms import CourseForm, CourseGroupForm
from .models import InstructorModel


def _scoped_instructor(request):
    """Re-fetch the instructor profile tied to the authenticated user only."""
    return (
        InstructorModel.objects
        .select_related('user')
        .get(pk=request.instructor.pk, user=request.user)
    )


def _instructor_courses_qs(instructor):
    """Courses assigned via FK or M2M — never other instructors' exclusive catalogue."""
    return (
        CourseModel.objects
        .filter(Q(instructor=instructor) | Q(pk__in=instructor.courses.values('pk')))
        .distinct()
    )


def _instructor_groups_qs(instructor):
    """Groups this instructor leads only — never another instructor's groups."""
    return CourseGroupModel.objects.filter(instructor=instructor)


def _get_owned_course(instructor, course_id):
    course = get_object_or_404(CourseModel, pk=course_id)
    if course.instructor_id != instructor.pk:
        raise Http404('Course not found.')
    return course


def _get_owned_group(instructor, group_id):
    return get_object_or_404(
        CourseGroupModel.objects.select_related('course'),
        pk=group_id,
        instructor=instructor,
    )


def _group_status(group, today):
    if group.start_date <= today <= group.end_date:
        return 'active'
    if today < group.start_date:
        return 'upcoming'
    return 'ended'


@instructor_required
def instructor_dashboard(request):
    instructor = _scoped_instructor(request)

    courses = list(_instructor_courses_qs(instructor).order_by('name'))

    groups = list(
        _instructor_groups_qs(instructor)
        .select_related('course')
        .annotate(student_count=Count('studentmodel', distinct=True))
        .order_by('-start_date', 'name')
    )

    today = timezone.localdate()
    active_groups_count = (
        _instructor_groups_qs(instructor)
        .filter(start_date__lte=today, end_date__gte=today)
        .count()
    )

    enrolled_students_count = (
        StudentModel.objects
        .filter(groups__instructor=instructor)
        .distinct()
        .count()
    )

    grades = (
        StudentGradeModel.objects
        .filter(group__instructor=instructor)
        .select_related('student', 'group', 'group__course')
        .order_by('-updated_at', '-created_at')
    )
    recent_grades = list(grades[:8])
    recent_grade_activity = grades.filter(
        updated_at__gte=timezone.now() - timedelta(days=30),
    ).count()

    context = {
        'instructor': instructor,
        'courses': courses,
        'groups': groups,
        'course_count': len(courses),
        'active_groups_count': active_groups_count,
        'enrolled_students_count': enrolled_students_count,
        'recent_grade_activity': recent_grade_activity,
        'recent_grades': recent_grades,
        'active_nav': 'dashboard',
    }
    return render(request, 'instructor_dashboard.html', context)


@instructor_required
def instructor_courses(request):
    instructor = _scoped_instructor(request)
    today = timezone.localdate()

    own_groups = Prefetch(
        'coursegroupmodel_set',
        queryset=(
            CourseGroupModel.objects
            .filter(instructor=instructor)
            .annotate(student_count=Count('studentmodel', distinct=True))
            .order_by('-start_date', 'name')
        ),
        to_attr='own_groups',
    )

    courses = list(
        _instructor_courses_qs(instructor)
        .annotate(
            own_group_count=Count(
                'coursegroupmodel',
                filter=Q(coursegroupmodel__instructor=instructor),
                distinct=True,
            ),
            own_student_count=Count(
                'coursegroupmodel__studentmodel',
                filter=Q(coursegroupmodel__instructor=instructor),
                distinct=True,
            ),
        )
        .prefetch_related(own_groups)
        .order_by('name')
    )

    total_groups = sum(course.own_group_count for course in courses)
    total_students = (
        StudentModel.objects
        .filter(groups__instructor=instructor, groups__course__in=[c.pk for c in courses])
        .distinct()
        .count()
        if courses else 0
    )
    active_groups_count = (
        _instructor_groups_qs(instructor)
        .filter(start_date__lte=today, end_date__gte=today)
        .count()
    )

    context = {
        'instructor': instructor,
        'courses': courses,
        'course_count': len(courses),
        'total_groups': total_groups,
        'total_students': total_students,
        'active_groups_count': active_groups_count,
        'active_nav': 'courses',
    }
    return render(request, 'instructor_courses.html', context)


@instructor_required
@require_http_methods(['GET', 'POST'])
def instructor_create_course(request):
    instructor = _scoped_instructor(request)

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = instructor
            course.save()
            instructor.courses.add(course)
            messages.success(request, f'Course “{course.name}” was created.')
            return redirect('instructor_courses')
    else:
        form = CourseForm(initial={'price': Decimal('0.00')})

    context = {
        'instructor': instructor,
        'form': form,
        'form_mode': 'create',
        'active_nav': 'courses',
    }
    return render(request, 'instructor_course_form.html', context)


def _course_edit_related_groups(course, instructor):
    related_groups = list(
        course.coursegroupmodel_set
        .filter(instructor=instructor)
        .annotate(student_count=Count('studentmodel', distinct=True))
        .order_by('-start_date', 'name')
    )
    today = timezone.localdate()
    for group in related_groups:
        group.status = _group_status(group, today)
    return related_groups


def _render_course_edit(
    request,
    instructor,
    course,
    form=None,
    group_form=None,
    show_create_group_modal=False,
):
    if form is None:
        form = CourseForm(instance=course)
    if group_form is None:
        group_form = CourseGroupForm(
            initial={'course': course.pk},
            course_queryset=CourseModel.objects.filter(pk=course.pk),
            lock_course=course,
        )

    context = {
        'instructor': instructor,
        'form': form,
        'group_form': group_form,
        'course': course,
        'related_groups': _course_edit_related_groups(course, instructor),
        'form_mode': 'edit',
        'show_create_group_modal': show_create_group_modal,
        'active_nav': 'courses',
    }
    return render(request, 'instructor_course_form.html', context)


@instructor_required
@require_http_methods(['GET', 'POST'])
def instructor_edit_course(request, course_id):
    instructor = _scoped_instructor(request)
    course = _get_owned_course(instructor, course_id)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save()
            instructor.courses.add(course)
            messages.success(request, f'Course “{course.name}” was updated.')
            return redirect('instructor_courses')
        return _render_course_edit(request, instructor, course, form=form)

    return _render_course_edit(request, instructor, course)


@instructor_required
@require_http_methods(['POST'])
def instructor_create_course_group(request, course_id):
    instructor = _scoped_instructor(request)
    course = _get_owned_course(instructor, course_id)
    group_form = CourseGroupForm(
        request.POST,
        course_queryset=CourseModel.objects.filter(pk=course.pk),
        lock_course=course,
    )

    if group_form.is_valid():
        group = group_form.save(commit=False)
        group.instructor = instructor
        group.course = course
        group.save()
        messages.success(request, f'Group “{group.name}” was created.')
        return redirect('instructor_edit_course', course_id=course.pk)

    return _render_course_edit(
        request,
        instructor,
        course,
        group_form=group_form,
        show_create_group_modal=True,
    )


@instructor_required
@require_http_methods(['GET', 'POST'])
def instructor_delete_course(request, course_id):
    instructor = _scoped_instructor(request)
    course = _get_owned_course(instructor, course_id)

    own_blocking_groups = list(
        course.coursegroupmodel_set
        .filter(instructor=instructor)
        .annotate(student_count=Count('studentmodel', distinct=True))
        .order_by('name')
    )
    other_groups_count = (
        course.coursegroupmodel_set
        .exclude(instructor=instructor)
        .count()
    )
    can_delete_course = not own_blocking_groups and other_groups_count == 0

    if request.method == 'POST':
        if not can_delete_course:
            messages.error(
                request,
                'Delete all groups on this course before you can remove the course.',
            )
            return redirect('instructor_delete_course', course_id=course.pk)
        name = course.name
        course.delete()
        messages.success(request, f'Course “{name}” was deleted.')
        return redirect('instructor_courses')

    context = {
        'instructor': instructor,
        'course': course,
        'blocking_groups': own_blocking_groups,
        'group_count': len(own_blocking_groups),
        'other_groups_count': other_groups_count,
        'can_delete_course': can_delete_course,
        'active_nav': 'courses',
    }
    return render(request, 'instructor_course_confirm_delete.html', context)


@instructor_required
def instructor_groups(request):
    instructor = _scoped_instructor(request)
    today = timezone.localdate()

    groups = list(
        _instructor_groups_qs(instructor)
        .select_related('course')
        .annotate(student_count=Count('studentmodel', distinct=True))
        .order_by('-start_date', 'name')
    )

    for group in groups:
        group.status = _group_status(group, today)

    active_count = sum(1 for group in groups if group.status == 'active')
    upcoming_count = sum(1 for group in groups if group.status == 'upcoming')
    ended_count = sum(1 for group in groups if group.status == 'ended')
    enrolled_students_count = (
        StudentModel.objects
        .filter(groups__instructor=instructor)
        .distinct()
        .count()
    )

    context = {
        'instructor': instructor,
        'groups': groups,
        'group_count': len(groups),
        'active_count': active_count,
        'upcoming_count': upcoming_count,
        'ended_count': ended_count,
        'enrolled_students_count': enrolled_students_count,
        'active_nav': 'groups',
    }
    return render(request, 'instructor_groups.html', context)


@instructor_required
@require_http_methods(['GET', 'POST'])
def instructor_create_group(request):
    instructor = _scoped_instructor(request)
    course_qs = _instructor_courses_qs(instructor)

    if not course_qs.exists():
        messages.error(request, 'Create a course before adding a group.')
        return redirect('instructor_create_course')

    if request.method == 'POST':
        form = CourseGroupForm(request.POST, course_queryset=course_qs)
        if form.is_valid():
            group = form.save(commit=False)
            group.instructor = instructor
            # Course must belong to this instructor's catalogue (form queryset enforces it).
            if not course_qs.filter(pk=group.course_id).exists():
                raise Http404('Course not found.')
            group.save()
            messages.success(request, f'Group “{group.name}” was created.')
            return redirect('instructor_groups')
    else:
        initial = {}
        course_id = request.GET.get('course')
        if course_id and course_qs.filter(pk=course_id).exists():
            initial['course'] = course_id
        form = CourseGroupForm(initial=initial, course_queryset=course_qs)

    context = {
        'instructor': instructor,
        'form': form,
        'form_mode': 'create',
        'active_nav': 'groups',
    }
    return render(request, 'instructor_group_form.html', context)


@instructor_required
@require_http_methods(['GET', 'POST'])
def instructor_edit_group(request, group_id):
    instructor = _scoped_instructor(request)
    group = _get_owned_group(instructor, group_id)
    course_qs = _instructor_courses_qs(instructor)

    if request.method == 'POST':
        form = CourseGroupForm(request.POST, instance=group, course_queryset=course_qs)
        if form.is_valid():
            group = form.save(commit=False)
            group.instructor = instructor
            if not course_qs.filter(pk=group.course_id).exists():
                raise Http404('Course not found.')
            group.save()
            messages.success(request, f'Group “{group.name}” was updated.')
            return redirect('instructor_groups')
    else:
        form = CourseGroupForm(instance=group, course_queryset=course_qs)

    related_students = list(
        StudentModel.objects
        .filter(groups=group)
        .select_related('user')
        .order_by('user__first_name', 'user__last_name')
    )
    grades_by_student = {
        grade.student_id: grade
        for grade in StudentGradeModel.objects.filter(group=group).select_related('student')
    }
    for student in related_students:
        student.group_grade = grades_by_student.get(student.user_id)

    available_students = list(
        StudentModel.objects
        .exclude(groups=group)
        .select_related('user')
        .order_by('user__first_name', 'user__last_name', 'register_number')
    )

    context = {
        'instructor': instructor,
        'form': form,
        'group': group,
        'related_students': related_students,
        'available_students': available_students,
        'form_mode': 'edit',
        'active_nav': 'groups',
    }
    return render(request, 'instructor_group_form.html', context)


@instructor_required
@require_http_methods(['POST'])
def instructor_add_group_student(request, group_id):
    instructor = _scoped_instructor(request)
    group = _get_owned_group(instructor, group_id)
    student = get_object_or_404(StudentModel.objects.select_related('user'), pk=request.POST.get('student_id'))

    if group.studentmodel_set.filter(pk=student.pk).exists():
        messages.error(request, f'{student.user.first_name} {student.user.last_name} is already in this group.')
    else:
        group.studentmodel_set.add(student)
        messages.success(
            request,
            f'{student.user.first_name} {student.user.last_name} was added to “{group.name}”.',
        )

    return redirect('instructor_edit_group', group_id=group.pk)


@instructor_required
@require_http_methods(['GET', 'POST'])
def instructor_delete_group(request, group_id):
    instructor = _scoped_instructor(request)
    group = _get_owned_group(instructor, group_id)
    student_count = group.studentmodel_set.count()
    grade_count = StudentGradeModel.objects.filter(group=group).count()

    if request.method == 'POST':
        name = group.name
        group.delete()
        messages.success(request, f'Group “{name}” was deleted.')
        return redirect('instructor_groups')

    context = {
        'instructor': instructor,
        'group': group,
        'student_count': student_count,
        'grade_count': grade_count,
        'active_nav': 'groups',
    }
    return render(request, 'instructor_group_confirm_delete.html', context)


@instructor_required
@require_http_methods(['GET', 'POST'])
def instructor_profile(request):
    instructor = _scoped_instructor(request)
    today = timezone.localdate()

    if request.method == 'POST':
        form = ContactProfileForm(request.POST, request.FILES, instance=instructor.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your contact details were updated.')
            return redirect('instructor_profile')
    else:
        form = ContactProfileForm(instance=instructor.user)

    course_count = _instructor_courses_qs(instructor).count()
    group_count = _instructor_groups_qs(instructor).count()
    active_groups_count = (
        _instructor_groups_qs(instructor)
        .filter(start_date__lte=today, end_date__gte=today)
        .count()
    )
    enrolled_students_count = (
        StudentModel.objects
        .filter(groups__instructor=instructor)
        .distinct()
        .count()
    )

    context = {
        'instructor': instructor,
        'form': form,
        'course_count': course_count,
        'group_count': group_count,
        'active_groups_count': active_groups_count,
        'enrolled_students_count': enrolled_students_count,
        'active_nav': 'profile',
    }
    return render(request, 'instructor_profile.html', context)
