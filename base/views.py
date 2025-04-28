from rest_framework import generics


class BaseAPIView(generics.GenericAPIView):
    """
    Base class to handle common patterns in API views.
    Subclasses should implement the `get_service` and
    optionally override `handle_request` for custom logic.
    """

    def handle_request(self, request, operation, *args, **kwargs):
        """
        Common handler for API operations.
        Args:
            request: The HTTP request.
            operation: The service method to call (e.g., `create`, `list`).
            *args: Additional positional arguments for the service method. The args must always be in the following (request.data, request.query_params)
            **kwargs: Additional keyword arguments for the service method.

        Returns:
            Response: DRF Response object.
        """
        # args += (request,)
        action = args[0]
        method = kwargs.get("method")
        if not method:
            method = operation

        service = self.get_service(request=request, method=method)
        id = kwargs.get("id")
        data, error, status_code = getattr(service, operation)(*args, **kwargs)

        if error:
            return service.error(error, f"{action.capitalize()} failed", status_code)
        return service.success(
            data=data,
            message=f"{action.capitalize()} successful",
            status_code=status_code,
            serializer=self.get_response_serializer_class(
                request=request, id=id, method=method
            ),
            request=request,
            view=self,
        )

    def get_service(self, *args, **kwargs):
        """
        Return the service instance. Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement the `get_service` method.")

    def get_serializer_class(self, *args, **kwargs):
        """
        Return the serializer class for the success response.
        Must be implemented by subclasses.
        """
        raise NotImplementedError(
            "Subclasses must implement the `get_serializer_class` method."
        )

    def get_response_serializer_class(self, *args, **kwargs):
        """
        Return the serializer class for the success response.
        Must be implemented by subclasses.
        """
        raise NotImplementedError(
            "Subclasses must implement the `get_serializer_class` method."
        )
