from django.urls import path

from account.views import auth

urlpatterns = [
    # auth urls
    path("login", auth.LoginAPIView.as_view(), name="login"),
    path("register", auth.LoginAPIView.as_view(), name="register"),
    path(
        "validate-login-otp", auth.OTPLoginAPIView.as_view(), name="validate-login-otp"
    ),
    path("logout", auth.LogoutAPIView.as_view(), name="logout"),
    path(
        "forgot-password", auth.ForgotPasswordAPIView.as_view(), name="forgot-password"
    ),
    path("reset-password", auth.ResetPasswordAPIView.as_view(), name="reset-password"),
    path("refresh-token", auth.RefreshTokenAPIView.as_view(), name="refresh-token"),
    path("activate-2fa", auth.TwoFactorActivateAPIView.as_view(), name="activate-2fa"),
    path(
        "deactivate-2fa",
        auth.TwoFactorDeactivateAPIView.as_view(),
        name="deactivate-2fa",
    ),
    path("mfa-status", auth.MFAStatusAPIView.as_view(), name="mfa-status"),
    path("verify-otp", auth.VerifyOTPAPIView.as_view(), name="verify-otp"),
    path(
        "change-user-password",
        auth.ChangeUserPasswordAPIView.as_view(),
        name="change-user-password",
    ),
]
