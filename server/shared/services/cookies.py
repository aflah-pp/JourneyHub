from django.conf import settings


class CookieService:

    REFRESH_COOKIE = "refresh_token"

    @classmethod
    def set_refresh_cookie(cls, response, token):
        response.set_cookie(
            key=cls.REFRESH_COOKIE,
            value=token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            max_age=60 * 60 * 24 * 7,
        )

    @classmethod
    def get_refresh_cookie(cls, request):
        return request.COOKIES.get(cls.REFRESH_COOKIE)

    @classmethod
    def clear_refresh_cookie(cls, response):
        response.delete_cookie(cls.REFRESH_COOKIE)
