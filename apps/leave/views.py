from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.contrib.auth.decorators import login_required

from django.contrib import messages

from .models import Leave

from apps.employees.models import Employee


@login_required
def leave_list(request):

    if request.user.role in ['SUPERVISOR', 'SUPERVISOR']:

        leaves = Leave.objects.select_related(
            'employee',
            'employee__user'
        ).all()

    else:

        employee = Employee.objects.filter(
            user=request.user
        ).first()

        leaves = Leave.objects.filter(
            employee=employee
        )

    context = {
        'leaves': leaves
    }

    return render(
        request,
        'leave/list.html',
        context
    )


@login_required
def apply_leave(request):

    employee = Employee.objects.filter(
        user=request.user
    ).first()

    if request.method == 'POST':

        Leave.objects.create(

            employee=employee,

            leave_type=request.POST.get(
                'leave_type'
            ),

            start_date=request.POST.get(
                'start_date'
            ),

            end_date=request.POST.get(
                'end_date'
            ),

            reason=request.POST.get(
                'reason'
            ),
        )

        messages.success(
            request,
            'Leave applied successfully.'
        )

        return redirect(
            'leave_list'
        )

    return render(
        request,
        'leave/apply.html'
    )


@login_required
def leave_detail(request, pk):

    leave = get_object_or_404(
        Leave,
        pk=pk
    )

    if request.method == 'POST':

        if request.user.role in ['SUPERVISOR', 'SUPERVISOR']:

            leave.status = request.POST.get(
                'status'
            )

            leave.save()

            messages.success(
                request,
                'Leave status updated.'
            )

            return redirect(
                'leave_list'
            )

    context = {
        'leave': leave
    }

    return render(
        request,
        'leave/detail.html',
        context
    )