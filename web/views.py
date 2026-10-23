from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import render

PAGES = {
    'home': {
        'title': 'Academy CRM',
        'description': 'Academy CRM keeps students, classes, and attendance in one place.',
    },
    'about': {
        'title': 'About · Academy CRM',
        'description': 'Academy CRM is a simple record for students, classes, and attendance.',
    },
    'contact': {
        'title': 'Contact · Academy CRM',
        'description': 'Send a message to Academy CRM.',
    },
}

EMPTY_FORM = {
    'name': '',
    'email': '',
    'message': '',
}


def _context(page, **extra):
    context = {
        'page': page,
        'title': PAGES[page]['title'],
        'description': PAGES[page]['description'],
        'form': EMPTY_FORM.copy(),
        'errors': {},
        'success': False,
        'submitted': None,
    }
    context.update(extra)
    return context


def _landing(request, page, **extra):
    return render(request, 'home.html', _context(page, **extra))


def home(request):
    return _landing(request, 'home')


def about(request):
    return _landing(request, 'about')


def _clean_contact(data):
    form = {
        'name': data.get('name', '').strip(),
        'email': data.get('email', '').strip(),
        'message': data.get('message', '').strip(),
    }
    errors = {}
    if not form['name']:
        errors['name'] = 'Enter your name.'
    try:
        validate_email(form['email'])
    except ValidationError:
        errors['email'] = 'Enter an email address like name@school.edu.'
    if len(form['message']) < 10:
        errors['message'] = 'Write at least 10 characters.'
    return form, errors


def contact(request):
    if request.method == 'POST':
        form, errors = _clean_contact(request.POST)
        if errors:
            return _landing(request, 'contact', form=form, errors=errors)
        return _landing(request, 'contact', success=True, submitted=form)
    return _landing(request, 'contact')


def _page(request, template, page, title, description, status=200):
    return render(request, template, {
        'page': page,
        'title': title,
        'description': description,
    }, status=status)


def terms(request):
    return _page(
        request,
        'terms.html',
        'terms',
        'Terms and conditions · Academy CRM',
        'Terms for using the Academy CRM website.',
    )


def privacy(request):
    return _page(
        request,
        'privacy.html',
        'privacy',
        'Privacy policy · Academy CRM',
        'How the Academy CRM website handles information you send.',
    )


def page_not_found(request, exception):
    return _page(
        request,
        '404.html',
        'not-found',
        'Page not found · Academy CRM',
        'This address is not part of Academy CRM.',
        status=404,
    )


def missing(request, resource):
    return page_not_found(request, resource)
