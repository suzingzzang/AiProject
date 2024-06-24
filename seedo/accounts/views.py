# accounts/views.py

from functools import wraps

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.decorators.csrf import csrf_protect

from .forms import CustomAuthenticationForm, CustomUserCreationForm
from .models import RefreshToken
from .utils import generate_tokens


class SignUpView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, "signup.html", {"form": form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")  # 적절한 리디렉션 URL로 변경
        return render(request, "signup.html", {"form": form})


class LoginView(View):
    def get(self, request):
        form = CustomAuthenticationForm()
        return render(request, "login.html", {"form": form})

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

        return render(request, "login.html", {"form": form})


def token_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")

        if not access_token or not refresh_token:
            return JsonResponse({"error": "Authentication required"}, status=401)

        try:
            decoded_token = jwt.decode(access_token, "seedo_project_key", algorithms=["HS256"])
            request.user_id = decoded_token["user_id"]
        except jwt.ExpiredSignatureError:
            try:
                decoded_refresh_token = jwt.decode(refresh_token, "seedo_project_key", algorithms=["HS256"])
                user_id = decoded_refresh_token["user_id"]
                refresh_token_instance = RefreshToken.objects.get(user_id=user_id, token=refresh_token)
                if refresh_token_instance.token_blacklist:
                    return JsonResponse({"error": "Refresh Token is blacklisted"}, status=401)

                new_access_token = jwt.encode({"user_id": user_id}, "seedo_project_key", algorithm="HS256")
                if isinstance(new_access_token, bytes):
                    new_access_token = new_access_token.decode("utf-8")

                response = JsonResponse({"access_token": new_access_token})
                response.set_cookie("access_token", new_access_token)
                return response
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, RefreshToken.DoesNotExist):
                return JsonResponse({"error": "Invalid or expired Refresh Token"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid Access Token"}, status=401)

        return view_func(request, *args, **kwargs)

    return wrapper


@token_required
def home(request):
    message = "Welcome to Home Page!!!"
    return render(request, "index.html", {"message": message})


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
    response = render(request, "login.html")
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return response
