from django.contrib.auth import (
    authenticate,
    login,
    logout
)

from django.contrib.auth.decorators import login_required

from django.shortcuts import (
    render,
    redirect
)

from .models import CompanySettings


def login_view(request):

    if request.user.is_authenticated:

        return redirect(
            'dashboard'
        )

    if request.method == 'POST':

        email = request.POST.get(
            'email'
        )

        password = request.POST.get(
            'password'
        )

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            return redirect(
                'dashboard'
            )

        return render(
            request,
            'accounts/login.html',
            {
                'error': 'Invalid email or password'
            }
        )

    return render(
        request,
        'accounts/login.html'
    )


@login_required
def dashboard_view(request):

    role = request.user.role

    if role == 'SUPERVISOR':

        return render(
            request,
            'dashboard/supervisor.html'
        )

    return render(
        request,
        'dashboard/employee.html'
    )


@login_required
def company_settings(request):

    settings_obj = CompanySettings.objects.first()

    if not settings_obj:

        settings_obj = CompanySettings.objects.create(

            company_name='SkillChekHub',

            company_address='Bangalore',

            company_email='admin@skillchekhub.com',

            company_phone='9999999999'

        )

    if request.method == 'POST':

        settings_obj.company_name = request.POST.get(
            'company_name'
        )

        settings_obj.company_address = request.POST.get(
            'company_address'
        )

        settings_obj.company_email = request.POST.get(
            'company_email'
        )

        settings_obj.company_phone = request.POST.get(
            'company_phone'
        )

        if request.FILES.get(
            'company_logo'
        ):

            settings_obj.company_logo = request.FILES.get(
                'company_logo'
            )

        settings_obj.save()

        return redirect(
            'company_settings'
        )

    return render(
        request,
        'settings/company.html',
        {
            'settings_obj': settings_obj
        }
    )


def logout_view(request):

    logout(
        request
    )

    return redirect(
        'login'
    )