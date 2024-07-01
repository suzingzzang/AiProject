from django.urls import path

from .views import LoginView, SignUpView, logout, profile

app_name = "accounts"

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", logout, name="account_logout"),
    path("", profile, name="mypage"),
]
