from functools import wraps

import jwt
from accounts.models import RefreshToken
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse


def token_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")

        if not access_token or not refresh_token:
            return HttpResponseRedirect(reverse("accounts:login"))

        try:
            decoded_token = jwt.decode(access_token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
            request.user_id = decoded_token["user_id"]
        except jwt.ExpiredSignatureError:
            try:
                decoded_refresh_token = jwt.decode(refresh_token, settings.JWT_REFRESH_SECRET_KEY, algorithms=["HS256"])
                user_id = decoded_refresh_token["user_id"]
                refresh_token_instance = RefreshToken.objects.get(user_id=user_id, token=refresh_token)
                if refresh_token_instance.token_blacklist:
                    return HttpResponseRedirect(reverse("accounts:login"))

                new_access_token = jwt.encode({"user_id": user_id}, settings.JWT_SECRET_KEY, algorithm="HS256")
                if isinstance(new_access_token, bytes):
                    new_access_token = new_access_token.decode("utf-8")

                response = view_func(request, *args, **kwargs)
                response.set_cookie("access_token", new_access_token)
                return response
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, RefreshToken.DoesNotExist):
                return HttpResponseRedirect(reverse("accounts:login"))
        except jwt.InvalidTokenError:
            return HttpResponseRedirect(reverse("accounts:login"))

        return view_func(request, *args, **kwargs)

    return wrapper
