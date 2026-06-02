from django.urls import path
from .views import (
    login_view,
    dashboard_view,
    logout_view,
    forgot_password,
    terms_view,
    privacy_view,
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('', dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('terms/', terms_view, name='terms'),
    path('privacy/', privacy_view, name='privacy'),
]