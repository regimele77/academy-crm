from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import StudentModel


def student_required(view_func):
    """Allow only authenticated users who have a StudentModel profile."""

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        student = (
            StudentModel.objects
            .select_related('user')
            .filter(user=request.user)
            .first()
        )
        if student is None:
            messages.error(request, 'Only students can access the student portal.')
            return redirect('home')
        request.student = student
        return view_func(request, *args, **kwargs)

    return _wrapped
