from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import User


MANAGEMENT_ACCESS_ROLES = {
    User.AccessRole.MASTER_ADMIN,
    User.AccessRole.FOUNDER,
    User.AccessRole.HR,
}

SELF_SERVICE_ROLES = {
    User.AccessRole.EMPLOYEE,
    User.AccessRole.CONTRACTOR,
}


def role_required(allowed_roles=None):
    """
    Access decorator supporting both the legacy SUPERVISOR role and the new
    access_role system.

    Compatibility behavior:
      SUPERVISOR -> any management account
      EMPLOYEE   -> employee or contractor self-service account
      MASTER_ADMIN always bypasses role restrictions
    """
    allowed_roles = set(allowed_roles or [])

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            access_role = getattr(
                request.user,
                'access_role',
                User.AccessRole.EMPLOYEE,
            )

            # Technical master admin can administer the entire HRMS.
            if access_role == User.AccessRole.MASTER_ADMIN:
                return view_func(request, *args, **kwargs)

            # Legacy supervisor rules now map to management roles.
            if 'SUPERVISOR' in allowed_roles:
                if access_role in MANAGEMENT_ACCESS_ROLES:
                    return view_func(request, *args, **kwargs)

            # Existing employee-only rules should also work for contractors.
            if 'EMPLOYEE' in allowed_roles:
                if access_role in SELF_SERVICE_ROLES:
                    return view_func(request, *args, **kwargs)

            # Exact new role matches.
            if access_role in allowed_roles:
                return view_func(request, *args, **kwargs)

            messages.error(
                request,
                'You do not have permission to access this page.'
            )
            return redirect('dashboard')

        return wrapper

    return decorator
