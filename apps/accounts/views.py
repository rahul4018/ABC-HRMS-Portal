from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


def login_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        return render(request, 'accounts/login.html', {
            'error': 'Invalid email or password'
        })

    return render(request, 'accounts/login.html')


@login_required
def dashboard_view(request):

    role = request.user.role

    if role == 'CEO':
        return render(request, 'dashboard/ceo.html')

    elif role == 'HR_ADMIN':
        return render(request, 'dashboard/hr.html')

    return render(request, 'dashboard/employee.html')


def logout_view(request):
    logout(request)
    return redirect('login')