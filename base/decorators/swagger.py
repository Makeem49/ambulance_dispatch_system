from functools import wraps
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from django.http import HttpRequest


def auto_schema_view(cls):
    """
    A class decorator that automatically applies swagger_auto_schema to all HTTP methods
    in the view, using get_serializer_class for payload and get_response_serializer_class for responses.
    Handles schema generation by inferring the method name.
    """
    http_methods = ["get", "post", "put", "patch", "delete"]

    for method_name in http_methods:
        if hasattr(cls, method_name):
            original_method = getattr(cls, method_name)

            @wraps(original_method)
            def wrapped_method(self, request=None, *args, **kwargs):
                method_upper = method_name.upper()
                id_param = kwargs.get("id")
                is_schema_generation = getattr(self, "swagger_fake_view", False)

                # Determine the HTTP method
                if is_schema_generation:
                    method_for_schema = method_upper
                else:
                    method_for_schema = request.method if request else method_upper

                # Get serializers
                if is_schema_generation:
                    request_serializer = self.get_serializer_class(
                        method=method_for_schema
                    )
                    response_serializer = self.get_response_serializer_class(
                        id=id_param, method=method_for_schema
                    )
                else:
                    request_serializer = self.get_serializer_class(request=request)
                    response_serializer = self.get_response_serializer_class(
                        request=request, id=id_param
                    )

                # Operation descriptions
                operation_descriptions = {
                    "get": "List all seasons or retrieve a specific season",
                    "post": "Create a new season",
                    "put": "Update a season",
                    "patch": "Partially update a season",
                    "delete": "Delete a season",
                }

                # Default response status codes and schemas
                responses = {
                    "get": {
                        200: (
                            response_serializer(many=(id_param is None))
                            if response_serializer
                            else "OK"
                        )
                    },
                    "post": {
                        201: response_serializer if response_serializer else "Created"
                    },
                    "put": {200: response_serializer if response_serializer else "OK"},
                    "patch": {
                        200: response_serializer if response_serializer else "OK"
                    },
                    "delete": {204: "No Content"},
                }

                # Swagger configuration
                swagger_params = {
                    "operation_description": operation_descriptions.get(
                        method_name, f"{method_name.capitalize()} operation"
                    ),
                    "responses": responses.get(method_name, {200: "OK"}),
                }

                # Add request body for methods with payload
                if method_upper in ["POST", "PUT", "PATCH"] and request_serializer:
                    swagger_params["request_body"] = request_serializer

                # Add query serializer for GET if applicable
                if method_upper == "GET" and request_serializer:
                    swagger_params["query_serializer"] = request_serializer

                # Apply swagger_auto_schema dynamically
                decorated_method = swagger_auto_schema(**swagger_params)(
                    original_method
                )
                return decorated_method(self, request, *args, **kwargs)

            setattr(cls, method_name, wrapped_method)

    return cls
