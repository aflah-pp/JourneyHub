from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class JWTService:

    @staticmethod
    def create_tokens(user):
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def blacklist_refresh_token(refresh_token):
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return True
        except TokenError:
            return False
