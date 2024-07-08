from django.urls import path

from .views import get_walking_directions, index

urlpatterns = [path("", index, name="index"), path("location/", get_walking_directions, name="get_pedestrian_directions")]
