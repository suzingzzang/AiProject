# camera/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.urls import path

from .views import fall_recognition, upload_recording

# from .views import depth_estimation


def index(request):
    return render(request, "camera/index.html")


app_name = "camera"

urlpatterns = [
    path("", index, name="show_camera"),
    path("upload/", upload_recording, name="upload_recording"),
    path("fall_recognition/", fall_recognition, name="fall_recognition"),
    # path("depth_estimation/", depth_estimation, name="depth_estimation"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
