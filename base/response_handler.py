from django.db.models.query import QuerySet
from rest_framework.response import Response
from rest_framework import status

from base.paginator_handler import CustomPagination


class ResponseHandler:
    @staticmethod
    def success(
        data=None,
        message="Success",
        status_code=status.HTTP_200_OK,
        serializer=None,
        request=None,
        view=None,
    ):
        """
        Return a standardized success response.

        :param data: Data to include in the response.
        :param message: A descriptive message for the success.
        :param status_code: HTTP status code (default: 200 OK).
        :return: Response object.
        """
        response_data = None
        if isinstance(data, QuerySet):
            paginator = CustomPagination()
            paginated_queryset = paginator.paginate_queryset(data, request, view=view)
            response_data = paginator.get_paginated_response(
                paginated_queryset, serializer, request
            )

        if not isinstance(data, QuerySet) and serializer:
            response_data = serializer(data).data

        data = response_data if response_data else data
        return Response(response_data, status_code)

    @staticmethod
    def error(
        errors=None,
        message="An error occurred",
        status_code=status.HTTP_400_BAD_REQUEST,
    ):
        """
        Return a standardized error response.

        :param errors: Error details or messages.
        :param message: A descriptive message for the error.
        :param status_code: HTTP status code (default: 400 BAD REQUEST).
        :return: Response object.
        """
        response = {
            "status": "error",
            "message": message,
            "errors": errors,
        }
        return Response(response, status_code)
