from django.shortcuts import render
from django.urls import path


def index(request):
    return render(request, "mypage/index.html")


app_name = "mypage"
urlpatterns = [path("", index, name="mypage")]
