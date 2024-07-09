"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from common.decorators import token_required
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path


@token_required
def index(request):
    return render(request, "index.html")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", index, name="home"),
    path("camera/", include("camera.urls")),
    path("matching/", include("matching.urls")),
    path("record/", include("record.urls")),
    path("qna/", include("qna.urls")),
    path("sensor/", include("sensor.urls")),
    path("nav/", include("navigation.urls")),
    path("walking_mode", include("walking_mode.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
