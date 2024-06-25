# accounts/views.py


import jwt
from common.decorators import token_required
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect, render
from django.views import View
from django.views.decorators.csrf import csrf_protect

from .forms import CustomAuthenticationForm, CustomUserCreationForm
from .models import RefreshToken
from .utils import generate_tokens


class SignUpView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, "accounts/signup.html", {"form": form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accounts:login")  # 적절한 리디렉션 URL로 변경
        return render(request, "accounts/signup.html", {"form": form})


class LoginView(View):
    def get(self, request):
        form = CustomAuthenticationForm()
        return render(request, "accounts/login.html", {"form": form})

    def post(self, request):
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, email=email, password=password)
            if user is not None:
                # 토큰 생성
                access_token, refresh_token = generate_tokens(user)

                # 리프레시 토큰 저장 또는 갱신
                refresh_token_instance, created = RefreshToken.objects.get_or_create(user=user)
                refresh_token_instance.token = refresh_token
                refresh_token_instance.token_blacklist = False
                refresh_token_instance.save()

                # 클라이언트 측에 토큰 저장
                response = redirect("home")
                response.set_cookie("access_token", access_token, max_age=settings.JWT_ACCESS_TOKEN_EXPIRATION)
                response.set_cookie("refresh_token", refresh_token, max_age=settings.JWT_REFRESH_TOKEN_EXPIRATION)
                return response

        return render(request, "accounts/login.html", {"form": form})


@token_required
def home(request):
    message = "Welcome to Home Page!!!"
    return render(request, "accounts/index.html", {"message": message})


@csrf_protect
def logout(request):
    refresh_token = request.COOKIES.get("refresh_token")
    if refresh_token:
        try:
            decoded_token = jwt.decode(refresh_token, "seedo_project_key", algorithms=["HS256"])
            refresh_token_instance = RefreshToken.objects.get(user_id=decoded_token["user_id"], token=refresh_token)
            refresh_token_instance.token_blacklist = True
            print(refresh_token_instance.token_blacklist, "refresh")
            refresh_token_instance.save()
        except (jwt.InvalidTokenError, RefreshToken.DoesNotExist):
            pass

    auth_logout(request)
    response = render(request, "accounts/login.html")
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return response
