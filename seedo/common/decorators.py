from functools import wraps

from accounts.models import RefreshToken
from common.utils import generate_new_access_token, verify_access_token, verify_refresh_token
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse


def token_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")

        if not access_token or not refresh_token:
            logout(request)
            return HttpResponseRedirect(reverse("accounts:login"))

        decoded_token = verify_access_token(access_token)
        if decoded_token:
            request.user_id = decoded_token["user_id"]
        else:
            decoded_refresh_token = verify_refresh_token(refresh_token)
            if decoded_refresh_token:
                user_id = decoded_refresh_token["user_id"]
                try:
                    refresh_token_instance = RefreshToken.objects.get(user_id=user_id, token=refresh_token)
                    if refresh_token_instance.token_blacklist:
                        logout(request)
                        return HttpResponseRedirect(reverse("accounts:login"))

                    new_access_token = generate_new_access_token(user_id)
                    if isinstance(new_access_token, bytes):
                        new_access_token = new_access_token.decode("utf-8")

                    response = view_func(request, *args, **kwargs)
                    response.set_cookie("access_token", new_access_token)
                    return response
                except RefreshToken.DoesNotExist:
                    logout(request)
                    return HttpResponseRedirect(reverse("accounts:login"))
            else:
                logout(request)
                return HttpResponseRedirect(reverse("accounts:login"))

        return view_func(request, *args, **kwargs)

    return wrapper
