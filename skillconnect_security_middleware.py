from django.shortcuts import redirect
from django.urls import reverse


class ForcePasswordChangeMiddleware:
    """Force users with a temporary password into the change-password flow."""

    EXEMPT_PREFIXES = (
        '/login/',
        '/logout/',
        '/change-password/',
        '/forgot-password/',
        '/static/',
        '/media/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        path = request.path or '/'

        if (
            user
            and user.is_authenticated
            and getattr(user, 'must_change_password', False)
            and not path.startswith(self.EXEMPT_PREFIXES)
        ):
            return redirect(f'{reverse("change_password")}?next={path}')

        return self.get_response(request)
