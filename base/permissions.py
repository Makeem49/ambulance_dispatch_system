from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated


class AuthUserMixin:
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


class NonAuthUserMixin:
    permission_classes = []
    authentication_classes = []
