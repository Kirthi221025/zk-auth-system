from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import HttpResponse


schema_view = get_schema_view(
    openapi.Info(
        title="ZK Authentication API",
        default_version='v1',
        description="Zero Knowledge Proof + JWT Authentication System",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def home(request):
    return HttpResponse("ZK Auth API is running successfully 🚀")


urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),

    # accounts API
    path('api/', include('accounts.urls')),

    # swagger documentation
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0)),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0)),
]