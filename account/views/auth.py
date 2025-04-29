from base.views import BaseAPIView
from account.serializers import auth
from base.service import ServiceFactory
from account.managers.auth import AuthenticationManager
from base.permissions import AuthUserMixin, NonAuthUserMixin


class BaseAuthAPIView(NonAuthUserMixin, BaseAPIView):
    """Base view class for authentication-related API endpoints."""

    serializer_classes = {
        "login": auth.LoginSerializer,
        "register": auth.RegistrationSerializer,
        "validate-login-otp": auth.TOTPLoginSerializer,
        "logout": auth.LogoutSerializer,
        "forgot-password": auth.ForgotPasswordSerializer,
        "reset-password": auth.ResetPasswordSerializer,
        "refresh-token": auth.RefreshTokenSerializer,
        "activate-2fa": auth.TwoFactorActivateSerializer,
        "deactivate-2fa": auth.TwoFactorDeactivateSerializer,
        "verify-otp": auth.VerifyTOTPSerializer,
        "mfa-status": None,
        "change-user-password": auth.ChangeUserPasswordSerializer
    }

    serializer_response_classes = {
        "login": auth.LoginResponseSerializer,
        "register": auth.RegistrationResponseSerializer,
        "validate-login-otp": auth.LoginResponseSerializer,
        "logout": auth.LogoutResponseSerializer,
        "forgot-password": auth.ForgetPasswordResponseSerializer,
        "reset-password": auth.ResetPasswordResponseSerializer,
        "refresh-token": auth.RefreshTokenResponseSerializer,
        "activate-2fa": auth.TwoFactorActivateResponseSerializer,
        "deactivate-2fa": auth.TwoFactorDeactivateResponseSerializer,
        "verify-otp": auth.VerifyTOTPResponseSerializer,
        "mfa-status": auth.TwoFactorActivateResponseSerializer,
        "change-user-password": auth.ResetPasswordResponseSerializer,
    }

    def get_service(self, *args, **kwargs):
        """Return service instance for authentication operations."""
        return ServiceFactory(
            AuthenticationManager,
            self.get_serializer_class(
                request=kwargs.get("request"), method=kwargs.get("method")
            ),
        )

    def get_serializer_class(self, *args, **kwargs):
        """Get appropriate serializer class based on HTTP method."""
        method = kwargs.get("method")
        return self.serializer_classes.get(method, None)

    def get_response_serializer_class(self, *args, **kwargs):
        """Get appropriate response serializer class based on HTTP method."""
        method = kwargs.get("method")
        return self.serializer_response_classes.get(method, None)


class LoginAPIView(BaseAuthAPIView):
    """Handle user login requests."""

    def post(self, request):
        """Process POST request for user login."""
        method = request.resolver_match.url_name
        return self.handle_request(
            request, "post", method, data=request.data, method=method
        )
        
class RegistrationAPIView(BaseAuthAPIView):
    """Handle patient account registration requests."""

    def post(self, request):
        """Process POST request for user login."""
        method = request.resolver_match.url_name
        return self.handle_request(
            request, "post", method, data=request.data, method=method
        )
        
class OTPLoginAPIView(BaseAuthAPIView):
    """Handle user login requests through totp."""

    def post(self, request):
        """Process POST request for user login."""
        method = request.resolver_match.url_name
        return self.handle_request(
            request, "post", method, data=request.data, method=method
        )


class LogoutAPIView(AuthUserMixin, BaseAuthAPIView):
    """Handle user logout requests."""

    def post(self, request):
        """Process POST request for user logout."""
        method = request.resolver_match.url_name
        return self.handle_request(
            request, "post", method, data=request.data, method=method
        )


class ForgotPasswordAPIView(BaseAuthAPIView):
    """Handle forgot password requests."""

    def post(self, request):
        """Process POST request for forgot password."""
        method = request.resolver_match.url_name
        return self.handle_request(
            request, "post", method, data=request.data, method=method
        )


class ResetPasswordAPIView(BaseAuthAPIView):
    """Handle password reset requests."""

    def post(self, request):
        """Process POST request for password reset."""
        method = request.resolver_match.url_name
        return self.handle_request(
            request, "post", method, data=request.data, method=method
        )


class RefreshTokenAPIView(AuthUserMixin, BaseAuthAPIView):
    """Handle token refresh requests."""

    def post(self, request):
        """Process POST request for token refresh."""
        method = request.resolver_match.url_name
        return self.handle_request(
            request, "post", method, data=request.data, method=method
        )


class TwoFactorActivateAPIView(AuthUserMixin, BaseAuthAPIView):
    """Handle 2FA activation requests."""

    def post(self, request):
        """Process POST request for 2FA activation."""
        method = request.resolver_match.url_name

        return self.handle_request(
            request, "post", method, data=request.data, method=method
        )


class TwoFactorDeactivateAPIView(AuthUserMixin, BaseAuthAPIView):
    """Handle 2FA deactivation requests."""

    def post(self, request):
        """Process POST request for 2FA deactivation."""
        method = request.resolver_match.url_name
        return self.handle_request(
            request, "post", method, data=request.data, method=method
        )


class MFAStatusAPIView(AuthUserMixin, BaseAuthAPIView):
    """Handle OTP status requests."""

    def get(self, request):
        """Process GET request for OTP status."""
        method = request.resolver_match.url_name
        return self.handle_request(
            request, "get", method, data=request.data, method=method
        )


class VerifyOTPAPIView(AuthUserMixin, BaseAuthAPIView):
    """Handle OTP verification requests."""

    def post(self, request):
        """Process POST request for OTP verification."""
        method = request.resolver_match.url_name
        return self.handle_request(
            request, "post", method, data=request.data, method=method
        )
        
class ChangeUserPasswordAPIView(AuthUserMixin, BaseAuthAPIView):
    """Handle User password update requests."""

    def post(self, request):
        """Process POST request for changing user password"""
        method = request.resolver_match.url_name
        return self.handle_request(
            request, "post", method, data=request.data, method=method
        )

