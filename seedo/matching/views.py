# matching/views.py

import json
import random

from common.decorators import token_required
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from twilio.rest import Client

from .models import UserRequest

User = get_user_model()


@token_required
def search_users(request):
    if request.method == "GET" and "email" in request.GET:
        email_query = request.GET.get("email")
        users = User.objects.filter(email__icontains=email_query).exclude(id=request.user.id).exclude(is_superuser=True)
        users_list = [{"id": user.id, "email": user.email} for user in users]
        return JsonResponse({"users": users_list})
    return JsonResponse({"error": "Invalid request"})


@token_required
def send_request(request):
    if request.method == "POST":
        data = json.loads(request.body)
        recipient_email = data.get("email")
        recipient = get_object_or_404(User, email=recipient_email)

        if recipient != request.user:
            # 이미 요청을 보냈는지 확인
            existing_request = UserRequest.objects.filter(requester=request.user, recipient=recipient).exists()
            if existing_request:
                return JsonResponse({"status": "error", "message": "이미 요청을 보냈습니다."}, status=400)

            Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            verification_code = str(random.randint(100000, 999999))  # 인증 코드 생성

            # SMS 보내기
            # message = client.messages.create(
            #    body=f'Your verification code is {verification_code}',
            #    from_=settings.TWILIO_PHONE_NUMBER,
            #    to=recipient.phonenumber
            # )
            # user_request =
            UserRequest.objects.create(requester=request.user, recipient=recipient, verification_code=verification_code)

            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "error", "message": "자신에게 요청을 보낼 수 없습니다."}, status=400)
    return JsonResponse({"status": "error", "message": "잘못된 요청입니다."}, status=400)


@token_required
def accept_request(request, request_id):
    if request.method == "POST":
        data = json.loads(request.body)
        verification_code = data.get("verification_code")
        user_request = get_object_or_404(UserRequest, id=request_id, recipient=request.user)

        if user_request.verification_code == verification_code:
            user_request.is_verified = True
            user_request.is_accepted = True
            user_request.save()
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "error", "message": "Invalid verification code"}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


@token_required
def remove_connection(request, request_id):
    user_request = get_object_or_404(UserRequest, id=request_id)
    if request.user == user_request.requester or request.user == user_request.recipient:
        user_request.delete()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Permission denied"})
