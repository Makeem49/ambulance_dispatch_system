from base.views import BaseAPIView
from ambulance_mgmt.serializers.ambulance import (
    AmbulanceCreateSerializer,
    AmbulanceListSerializer,
    AmbulanceUpdateSerializer,
    AmbulanceDetailSerializer,
    AmbulancePartialUpdateSerializer,
)
from base.service import ServiceFactory
from ambulance_mgmt.managers.ambulance import AmbulanceManager


class BaseAmbulanceAPIView(BaseAPIView):
    serializer_classes = {
        "get": None,
        "post": AmbulanceCreateSerializer,
        "put": AmbulanceUpdateSerializer,
        "patch": AmbulancePartialUpdateSerializer,
        "delete": None,
    }

    serializer_response_classes = {
        "get": AmbulanceListSerializer,
        "post": AmbulanceListSerializer,
        "put": AmbulanceDetailSerializer,
        "patch": AmbulanceDetailSerializer,
        "delete": AmbulanceDetailSerializer,
    }

    def get_service(self, *args, **kwargs):
        request = kwargs.get("request")
        return ServiceFactory(
            AmbulanceManager, self.get_serializer_class(request=request)
        )

    def get_serializer_class(self, *args, **kwargs):
        request = kwargs.get("request")
        method_to_action = {
            "GET": "get",
            "POST": "post",
            "PUT": "put",
            "PATCH": "patch",
            "DELETE": "delete",
        }
        action = method_to_action.get(request.method, "get")
        return self.serializer_classes.get(action, None)

    def get_response_serializer_class(self, *args, **kwargs):
        request = kwargs.get("request")
        instance_id = kwargs.get("id")
        if request.method == "GET" and id:
            return AmbulanceDetailSerializer

        method_to_action = {
            "GET": "get",
            "POST": "post",
            "PUT": "put",
            "PATCH": "patch",
            "DELETE": "delete",
        }
        action = method_to_action.get(request.method)
        return self.serializer_response_classes.get(action, None)


class AmbulanceAPIView(BaseAmbulanceAPIView):
    def get(self, request, id=None):
        action = request.resolver_match.url_name
        return self.handle_request(
            request, "get", action, query_params=request.query_params, id=id
        )

    def post(self, request):
        action = request.resolver_match.url_name
        return self.handle_request(
            request,
            "post",
            action,
            data=request.data,
            query_params=request.query_params,
        )

    def put(self, request, id):
        action = request.resolver_match.url_name
        return self.handle_request(
            request,
            "put",
            action,
            data=request.data,
            query_params=request.query_params,
            id=id,
        )

    def patch(self, request, id):
        action = request.resolver_match.url_name
        return self.handle_request(
            request,
            "patch",
            action,
            data=request.data,
            query_params=request.query_params,
            id=id,
        )

    def delete(self, request, id):
        action = request.resolver_match.url_name
        return self.handle_request(request, "delete", action, id=id)
