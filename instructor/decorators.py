from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import InstructorModel


def instructor_required(view_func):
    """Allow only authenticated users who have an InstructorModel profile."""

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        instructor = (
            InstructorModel.objects
            .select_related('user')
            .filter(user=request.user)
            .first()
        )
        if instructor is None:
            messages.error(request, 'Only instructors can access the instructor portal.')
            return redirect('home')
        request.instructor = instructor
        return view_func(request, *args, **kwargs)

    return _wrapped
