from django.urls import path
from .views import index,get_walking_directions

urlpatterns = [
    path('', index, name='index'),
    path('location/', get_walking_directions, name='get_pedestrian_directions'),
]