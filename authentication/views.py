from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import redirect

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Welcome back, {user.first_name}!')
            return redirect('home')
        messages.error(request, 'Invalid email or password')
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    list(messages.get_messages(request)) 
    messages.success(request, 'Logout successful')
    return redirect('login')

