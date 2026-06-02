from .models import CompanySettings

def company_settings_processor(request):
    """
    A Django context processor that injects company global variables 
    (like branding name, support email, and logo) into every template context.
    """
    # Safely retrieve the first configuration record
    settings_obj = CompanySettings.objects.first()

    return {
        'global_company_settings': settings_obj
    }