# accounts/utils.py

from datetime import datetime

import jwt
from accounts.models import RefreshToken
from django.conf import settings


def generate_tokens(user):
    # Access Token 생성
    access_payload = {"user_id": user.id, "exp": datetime.utcnow() + settings.JWT_ACCESS_TOKEN_EXPIRATION, "iat": datetime.utcnow()}
    access_token = jwt.encode(access_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # Refresh Token 생성
    refresh_payload = {"user_id": user.id, "exp": datetime.utcnow() + settings.JWT_REFRESH_TOKEN_EXPIRATION, "iat": datetime.utcnow()}
    refresh_token = jwt.encode(refresh_payload, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # Refresh Token 저장
    token, created = RefreshToken.objects.get_or_create(user=user)
    token.token = refresh_token  # 문자열로 디코딩할 필요 없음
    token.token_blacklist = False
    token.save()

    return access_token, refresh_token


def verify_access_token(token):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def verify_refresh_token(token):
    try:
        payload = jwt.decode(token, settings.JWT_REFRESH_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def generate_new_access_token(user_id):
    # Access Token 생성
    access_payload = {"user_id": user_id, "exp": datetime.utcnow() + settings.JWT_ACCESS_TOKEN_EXPIRATION, "iat": datetime.utcnow()}
    access_token = jwt.encode(access_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return access_token
