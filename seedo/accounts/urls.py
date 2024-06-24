from django.urls import path

from .views import LoginView, SignUpView, home, logout

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("", home, name="home"),
    path("logout/", logout, name="account_logout"),
]
