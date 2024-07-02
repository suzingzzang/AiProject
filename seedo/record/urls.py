from common.decorators import token_required
from django.shortcuts import render
from django.urls import path

from .views import *


@token_required
def page_break(request):
    return render(request, "record/break.html")


@token_required
def page_accident(request):
    return render(request, "record/accident.html")


app_name = "record"

urlpatterns = [
    path("break/", page_break, name="break"),
    path("accident/", page_accident, name="accident"),
    path("break/<int:request_id>/", broken_view, name="broken_list"),
]
