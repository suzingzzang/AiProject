from common.decorators import token_required
from django.shortcuts import render
from django.urls import path

from .views import LoginView, SignUpView, logout


@token_required
def index(request):
    return render(request, "accounts/index.html")


app_name = "accounts"

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", logout, name="account_logout"),
    path("", index, name="mypage"),
]
