from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import JobRequirement, Applicant
from apps.accounts.models import User

from apps.employees.models import (
    Employee,
    Department
)
@login_required
def requirement_list(request):
    requirements = JobRequirement.objects.all().order_by('-created_at')
    return render(
        request,
        'recruitment/requirements.html',
        {'requirements': requirements}
    )


@login_required
def create_requirement(request):
    if request.method == 'POST':
        # Retrieve form data
        title = request.POST.get('title')
        department = request.POST.get('department')
        openings = request.POST.get('openings')
        experience = request.POST.get('experience')
        description = request.POST.get('description')

        # Basic Validation Safeguard
        if not all([title, department, openings, experience]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'recruitment/create_requirement.html')

        JobRequirement.objects.create(
            title=title,
            department=department,
            openings=openings,
            experience=experience,
            description=description
        )
        
        messages.success(request, 'Requirement created successfully.')
        return redirect('requirement_list')

    return render(request, 'recruitment/create_requirement.html')


@login_required
def applicant_list(request, requirement_id):
    requirement = get_object_or_404(JobRequirement, pk=requirement_id)
    applicants = Applicant.objects.filter(requirement=requirement)
    
    return render(
        request,
        'recruitment/applicants.html',
        {
            'requirement': requirement,
            'applicants': applicants
        }
    )


@login_required
@require_POST  # Secure state-change actions
def shortlist_applicant(request, pk):
    applicant = get_object_or_404(Applicant, pk=pk)
    applicant.status = 'SHORTLISTED'
    applicant.save()

    messages.success(request, f'{applicant.full_name} shortlisted.')
    return redirect('applicant_list', requirement_id=applicant.requirement.pk)


@login_required
@require_POST
def select_applicant(request, pk):
    applicant = get_object_or_404(Applicant, pk=pk)
    applicant.status = 'SELECTED'
    applicant.save()

    messages.success(request, f'{applicant.full_name} selected.')
    return redirect('applicant_list', requirement_id=applicant.requirement.pk)


@login_required
@require_POST
def onboard_applicant(request, pk):
    applicant = get_object_or_404(Applicant, pk=pk)
    applicant.status = 'ONBOARDED'
    applicant.save()

    messages.success(request, f'{applicant.full_name} onboarded successfully.')
    return redirect('applicant_list', requirement_id=applicant.requirement.pk)

@login_required
def convert_to_employee(request, pk):

    applicant = get_object_or_404(
        Applicant,
        pk=pk
    )

    if applicant.employee_created:

        messages.warning(
            request,
            'Employee already created.'
        )

        return redirect(
            'applicant_list',
            applicant.requirement.id
        )

    user = User.objects.create_user(

        username=applicant.email,

        email=applicant.email,

        password='Welcome@123',

        role='EMPLOYEE'

    )

    department = Department.objects.first()

    Employee.objects.create(

        user=user,

        employee_id=f"EMP{user.id:04d}",

        department=department,

        designation=applicant.requirement.title,

        status='ACTIVE'

    )

    applicant.employee_created = True

    applicant.save()

    messages.success(
        request,
        'Employee created successfully.'
    )

    return redirect(
        'applicant_list',
        applicant.requirement.id
    )