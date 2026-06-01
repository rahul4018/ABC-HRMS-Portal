from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied

from .models import CompanySettings

def login_view(request):
    # 1. If user is already logged in, send them straight to the dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    # 2. Handle form submission (POST)
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        selected_role = request.POST.get('role', 'SUPERVISOR')

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:
            # Role validation logic
            if selected_role == 'SUPERVISOR' and user.role != 'SUPERVISOR':
                return render(
                    request,
                    'accounts/login.html',
                    {'error': 'This account is not a Supervisor account.'}
                )

            if selected_role == 'EMPLOYEE' and user.role == 'SUPERVISOR':
                return render(
                    request,
                    'accounts/login.html',
                    {'error': 'Please use Supervisor login.'}
                )

            # Log the user in if roles match
            login(request, user)
            return redirect('dashboard')
        
        # If authentication fails
        return render(
            request,
            'accounts/login.html',
            {'error': 'Invalid email or password.'}
        )

    # 3. Handle initial page load (GET request)
    return render(request, 'accounts/login.html')


@login_required
def dashboard_view(request):
    role = getattr(request.user, 'role', 'EMPLOYEE') # Fallback safe check

    if role == 'SUPERVISOR':
        return render(request, 'dashboard/supervisor.html')

    return render(request, 'dashboard/employee.html')


@login_required
def company_settings(request):
    # Security Check: Only allow Supervisors to access/edit company settings
    if getattr(request.user, 'role', None) != 'SUPERVISOR':
        raise PermissionDenied("You do not have permission to access this page.")

    # Get or create the initial settings record object
    settings_obj = CompanySettings.objects.first()
    if not settings_obj:
        settings_obj = CompanySettings.objects.create(
            company_name='SkillCheckHub',
            company_address='Bangalore',
            company_email='admin@skillcheckhub.com',
            company_phone='9999999999'
        )

    if request.method == 'POST':
        settings_obj.company_name = request.POST.get('company_name')
        settings_obj.company_address = request.POST.get('company_address')
        settings_obj.company_email = request.POST.get('company_email')
        settings_obj.company_phone = request.POST.get('company_phone')

        if request.FILES.get('company_logo'):
            settings_obj.company_logo = request.FILES.get('company_logo')

        settings_obj.save()
        return redirect('company_settings')

    return render(
        request,
        'settings/company.html',
        {'settings_obj': settings_obj}
    )


def logout_view(request):
    logout(request)
    return redirect('login')