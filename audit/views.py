from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import AuditLog

@login_required
def audit_list(request):
    # Fixed indentation and added ordering to show newest logs first
    logs = AuditLog.objects.select_related('user').all().order_by('-created_at')

    return render(
        request,
        'audit/list.html',
        {'logs': logs}
    )