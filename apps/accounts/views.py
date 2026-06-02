import random
import string
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from .models import CompanySettings


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        selected_role = request.POST.get('role', 'SUPERVISOR')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            user_role = getattr(user, 'role', None)

            if selected_role == 'SUPERVISOR' and user_role != 'SUPERVISOR':
                messages.error(request, 'This account is not a Supervisor account.')
                return render(request, 'accounts/login.html')

            if selected_role == 'EMPLOYEE' and user_role == 'SUPERVISOR':
                messages.error(request, 'Please login through Supervisor portal.')
                return render(request, 'accounts/login.html')

            login(request, user)
            return redirect('dashboard')

        messages.error(request, 'Invalid email or password.')

    return render(request, 'accounts/login.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        User = get_user_model()
        user = User.objects.filter(email=email).first()

        if not user:
            messages.error(request, 'No account found with this email.')
            return render(request, 'accounts/forgot_password.html')

        temporary_password = ''.join(
            random.choices(string.ascii_letters + string.digits, k=8)
        )
        user.password = make_password(temporary_password)
        user.save()

        return render(
            request,
            'accounts/forgot_password.html',
            {'temporary_password': temporary_password}
        )

    return render(
        request, 
        'accounts/forgot_password.html'
    )


@login_required
def dashboard_view(request):
    role = getattr(request.user, 'role', 'EMPLOYEE')

    if role == 'SUPERVISOR':
        return render(request, 'dashboard/supervisor.html')

    return render(request, 'dashboard/employee.html')


@login_required
def company_settings(request):
    if getattr(request.user, 'role', None) != 'SUPERVISOR':
        raise PermissionDenied("You do not have permission to access company settings.")

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

        # Files must be pulled from request.FILES, not request.POST
        if request.FILES.get('company_logo'):
            settings_obj.company_logo = request.FILES.get('company_logo')

        settings_obj.save()
        messages.success(request, 'Company settings updated successfully.')
        return redirect('company_settings')

    return render(
        request,
        'settings/company.html',
        {'settings_obj': settings_obj}
    )


def terms_view(request):
    return render(request, 'legal/terms.html')


def privacy_view(request):
    return render(request, 'legal/privacy.html')


def logout_view(request):
    logout(request)
    return redirect('login')