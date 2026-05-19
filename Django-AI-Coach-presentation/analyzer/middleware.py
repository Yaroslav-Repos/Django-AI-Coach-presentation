from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin

User = get_user_model()

@database_sync_to_async
def get_user_from_token(token_key):
    try:
        access_token = AccessToken(token_key)
        return User.objects.get(id=access_token['user_id'])
    except (InvalidToken, TokenError, User.DoesNotExist):
        return AnonymousUser()


class JWTCookieAuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        access_token = request.COOKIES.get('access_token')

        if access_token:
            try:
                token = AccessToken(access_token)
                user_id = token.get('user_id')
                request.user = User.objects.get(id=user_id)
                return None
            except (InvalidToken, TokenError, User.DoesNotExist):
                request.user = AnonymousUser()
                return None

        return None

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):

        headers = dict(scope.get("headers", []))
        cookie_header = headers.get(b"cookie", b"").decode("utf-8")

        cookies = {}
        for item in cookie_header.split(";"):
            if "=" in item:
                key, val = item.strip().split("=", 1)
                cookies[key] = val

        token = cookies.get("access_token")

        if token:
            scope["user"] = await get_user_from_token(token)
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)

