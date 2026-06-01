from django.shortcuts import render, redirect
from apps.employees.models import Employee
from .models import Promotion


def promotion_list(request):

    promotions = Promotion.objects.select_related(
        'employee',
        'employee__user'
    ).all().order_by('-created_at')

    return render(
        request,
        'promotions/list.html',
        {
            'promotions': promotions
        }
    )


def create_promotion(request):

    if request.method == 'POST':

        employee = Employee.objects.get(
            id=request.POST.get('employee')
        )

        Promotion.objects.create(
            employee=employee,
            old_designation=request.POST.get('old_designation'),
            new_designation=request.POST.get('new_designation'),
            effective_date=request.POST.get('effective_date'),
            remarks=request.POST.get('remarks')
        )

        return redirect('promotion_list')

    employees = Employee.objects.all()

    return render(
        request,
        'promotions/create.html',
        {
            'employees': employees
        }
    )