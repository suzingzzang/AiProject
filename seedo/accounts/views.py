# accounts/views.py


import jwt
from common.decorators import token_required
from common.utils import generate_tokens
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views import View
from django.views.decorators.csrf import csrf_protect
from matching.models import UserRequest

from .forms import CustomAuthenticationForm, CustomUserCreationForm
from .models import RefreshToken


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
            logout(request)
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, email=email, password=password)
            if user is not None:
                # 토큰 생성
                access_token, refresh_token = generate_tokens(user)

                # 세션을 사용하여 request.user 설정
                auth_login(request, user)

                # 클라이언트 측에 토큰 저장
                response = redirect("home")
                response.set_cookie("access_token", access_token)
                response.set_cookie("refresh_token", refresh_token)
                return response

        return render(request, "accounts/login.html", {"form": form})


@csrf_protect
def logout(request):
    refresh_token = request.COOKIES.get("refresh_token")
    if refresh_token:
        try:
            decoded_token = jwt.decode(refresh_token, "seedo_project_key", algorithms=["HS256"])
            refresh_token_instance = RefreshToken.objects.get(user_id=decoded_token["user_id"], token=refresh_token)
            refresh_token_instance.token_blacklist = True
            refresh_token_instance.save()
        except (jwt.InvalidTokenError, RefreshToken.DoesNotExist):
            pass

    auth_logout(request)

    if request.headers["Referer"][30:] != "/login/":
        response = redirect("accounts:login")
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


@token_required
def profile(request):
    user = request.user
    # 사용자가 보낸 요청과 받은 요청을 모두 필터링
    user_requests = UserRequest.objects.filter(Q(requester=user) | Q(recipient=user))

    partner_list = []

    for user_request in user_requests:
        partner_info = {
            "user": user_request.recipient if user_request.requester == user else user_request.requester,
            "request_id": user_request.id,
            "is_accepted": user_request.is_accepted,
            "is_verified": user_request.is_verified,
            "is_requester": user_request.requester == user,
        }
        partner_list.append(partner_info)

    context = {"user": user, "partner_list": partner_list}
    return render(request, "accounts/index.html", context)
