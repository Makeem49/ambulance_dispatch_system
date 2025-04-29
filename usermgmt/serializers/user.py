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


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["username", "created", "updated", "password"]



class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password"]


class DeleteUserSerializer(serializers.Serializer):
    message = serializers.CharField()
