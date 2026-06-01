from .models import AuditLog

def create_audit_log(user, module, action):
    """
    Safely creates an audit log tracking entry in the database.
    Supports anonymous or unauthenticated users by checking authentication status.
    """
    # Safeguard: If the user isn't logged in or is anonymous, store as None
    log_user = user if (user and user.is_authenticated) else None

    AuditLog.objects.create(
        user=log_user,
        module=module,
        action=action
    )