from django.urls import path
from .views import get_challenge, verify

urlpatterns = [
    path('get_challenge/', get_challenge),
    path('verify/', verify),
]