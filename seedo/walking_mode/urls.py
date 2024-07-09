from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import *
from .views import ImageUploadView


def index(request):
    return render(request, "walking_mode/test2.html")


app_name = "walking_mode"

urlpatterns = [path("", ImageUploadView.as_view(), name="test"), path("", index, name="show_camera")]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
