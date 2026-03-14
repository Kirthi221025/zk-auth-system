from django.urls import path
from .views import (
    register,
    get_challenge,
    verify_proof,
    dashboard,
    logout,
    refresh_token,
    admin_panel
)

urlpatterns = [
    path('register/', register),
    path('get_challenge/', get_challenge),
    path('verify/', verify_proof),
    path('refresh/', refresh_token),
    path('dashboard/', dashboard),
    path('logout/', logout),
    path('admin_panel/', admin_panel),
]