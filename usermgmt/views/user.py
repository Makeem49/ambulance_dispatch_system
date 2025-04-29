from base.views import BaseAPIView
from usermgmt.serializers.user import (
    UserListSerializer,
    UserUpdateSerializer,
    UserDetailSerializer,
    DeleteUserSerializer,
    AddUserSerializer,
)
from account.serializers.auth import RegistrationResponseSerializer
from base.service import ServiceFactory
from usermgmt.managers.user import UserManager


class BaseUserAPIView(BaseAPIView):
    serializer_classes = {
        "get": None,
        "post": AddUserSerializer,
        "put": UserUpdateSerializer,
        "delete": None,
    }

    serializer_response_classes = {
        "get": UserListSerializer,
        "post": RegistrationResponseSerializer,
        "put": UserDetailSerializer,
        "delete": DeleteUserSerializer,
    }

    def get_service(self, *args, **kwargs):
        return ServiceFactory(
            UserManager, self.get_serializer_class(request=kwargs.get("request"))
        )

    def get_serializer_class(self, *args, **kwargs):
        method_to_action = {
            "GET": "get",
            "POST": "post",
            "PUT": "put",
            "PATCH": "patch",
            "DELETE": "delete",
        }
        request = kwargs.get("request")
        action = method_to_action.get(request.method, "get")
        return self.serializer_classes.get(action, None)

    def get_response_serializer_class(self, *args, **kwargs):
        id = kwargs.get("id")
        request = kwargs.get("request")
        if request.method == "GET" and id:
            return UserDetailSerializer

        method_to_action = {
            "GET": "get",
            "POST": "post",
            "PUT": "put",
            "PATCH": "patch",
            "DELETE": "delete",
        }

        action = method_to_action.get(request.method)
        return self.serializer_response_classes.get(action, None)


class UserAPIView(BaseUserAPIView):
    def get(self, request, id=None):
        action = "List Users" if id is None else "Get User"
        return self.handle_request(
            request, "get", action, query_params=request.query_params, id=id
        )

    def post(self, request):
        action = "Create User"
        return self.handle_request(
            request,
            "post",
            action,
            data=request.data,
            query_params=request.query_params,
        )

    def put(self, request, id):
        action = "Update User"
        return self.handle_request(
            request,
            "put",
            action,
            data=request.data,
            query_params=request.query_params,
            id=id,
        )

    def delete(self, request, id):
        action = "Delete User"
        return self.handle_request(request, "delete", action, id=id)
