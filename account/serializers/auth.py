from rest_framework import serializers
from account.models import User
from account.models.users import ROLE_CHOICES


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        username = data.get("username")

        if email and username:
            raise serializers.ValidationError(
                "Please provide either email or username, not both"
            )
        if not email and not username:
            raise serializers.ValidationError("Please provide either email or username")

        return data


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        exclude = ["username", "created", "updated", "is_mfa_enabled", "role"]


class RegistrationResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "emergency_first_name",
            "emergency_last_name",
            "emergency_phone_number",
        ]


class TOTPLoginSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)
    otp = serializers.CharField(max_length=6, min_length=6)


class LoginResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=False)
    refresh_token = serializers.CharField(required=False)
    message = serializers.CharField(required=False)
    requires_2fa = serializers.CharField(required=False)
    mfa_url = serializers.CharField(required=False)


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class LogoutResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ForgetPasswordResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    otp = serializers.CharField()


class ResetPasswordResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class LockAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()


class LockAccountResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class RefreshTokenResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    message = serializers.CharField()


class TwoFactorActivateSerializer(serializers.Serializer):
    activate_totp = serializers.BooleanField(required=True)


class TwoFactorActivateResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    otp_auth_url = serializers.CharField()
    verified = serializers.BooleanField()


class TwoFactorDeactivateSerializer(serializers.Serializer):
    deactivate_totp = serializers.BooleanField(required=True)


class TwoFactorDeactivateResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class VerifyTOTPSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=6, min_length=6)


class VerifyTOTPResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    verified = serializers.BooleanField()


class ChangeUserPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=False)
    new_password = serializers.CharField(required=True)
    token = serializers.CharField(required=False)

    def validate(self, data):
        old_password = data.get("old_password")
        token = data.get("token")

        if old_password and token:
            raise serializers.ValidationError(
                "Please provide either old_password for user with no mfa activated or token for user with mfa activated, not both"
            )

        if not old_password and not token:
            raise serializers.ValidationError(
                "Please provide either old_password for user with no mfa activated or token for user with mfa activated, not both"
            )

        return data
