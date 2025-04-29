from rest_framework import serializers
from account.models import User
from account.models.users import ROLE_CHOICES
from base.utils.password_checker import check_password


class AddUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True)
    role = serializers.ChoiceField(required=True, choices=ROLE_CHOICES.values)

    class Meta:
        model = User
        exclude = ["username", "created", "updated", "is_mfa_enabled"]


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "created",
            "updated",
        ]


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "created"]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "is_staff",
            "is_2fa_enabled",
            "is_email_verified",
            "bio",
            "website",
            "reading_preferences",
        ]


class UserPartialUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def __init__(self, instance=None, data=..., **kwargs):
        print("hello")
        super().__init__(instance, data, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].required = False


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password"]


class DeleteUserSerializer(serializers.Serializer):
    message = serializers.CharField()
