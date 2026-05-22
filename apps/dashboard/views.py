from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):

    if request.user.role == 'CEO':
        return render(
            request,
            'dashboard/ceo.html'
        )

    elif request.user.role == 'HR':
        return render(
            request,
            'dashboard/hr.html'
        )

    return render(
        request,
        'dashboard/employee.html'
    )