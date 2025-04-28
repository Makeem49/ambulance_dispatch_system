from rest_framework import status
from base import data_validator, response_handler
from crequest.middleware import CrequestMiddleware


class CRUDService(data_validator.DataValidator):
    """
    Provides CRUD operations while integrating data validation.
    """

    def __init__(self, manager=None, serializer=None):
        """Initialize with manager and serializer."""
        super().__init__(serializer)
        self.manager = manager

    def post(self, *args, **kwargs):
        """
        Create a new resource.

        Args:
            data (dict): Data for the resource.

        Returns:
            tuple: (instance, error, status_code) - The created instance or validation errors.
                                                   Any error return by serializer is 400
        """
        current_request = CrequestMiddleware.get_request()
        data = kwargs.get("data")
        self.validate(data)
        if self.errors:
            return None, self.errors, 400
        kwargs["data"] = self.valid_data
        kwargs["request"] = current_request
        return self.manager.post(*args, **kwargs)

    def put(self, *args, **kwargs):
        """
        Update an existing resource.

        Args:
            data (dict): Data for updating the resource.

        Returns:
            tuple: (instance, error status_code) - The created instance or validation errors.
                                                  Any error return by serializer is 400
        """
        data = kwargs.get("data")
        instance_id = kwargs.get("id")
        instance, error = self.manager.repository.get_by_id_or_filter_condition(
            id=instance_id
        )
        current_request = CrequestMiddleware.get_request()

        if error:
            return None, error, status.HTTP_404_NOT_FOUND

        self.validate(data, instance, partial=False)
        if self.errors:
            return None, self.errors, 400
        kwargs["data"] = self.valid_data
        kwargs["id"] = instance_id
        kwargs["request"] = current_request
        return self.manager.put(*args, **kwargs)

    def patch(self, *args, **kwargs):
        """
        Partially update an existing resource.

        Args:
            data (dict): Data for partial updates.

        Returns:
            tuple: (instance, error, status_code) - The created instance or validation errors.
                                                    Any error return by serializer is 400
        """
        data = kwargs.get("data")
        instance_id = kwargs.get("id")
        instance, error = self.manager.repository.get_by_id_or_filter_condition(
            id=instance_id
        )
        current_request = CrequestMiddleware.get_request()

        if error:
            return None, error, status.HTTP_404_NOT_FOUND

        self.validate(data, instance, partial=True)

        if self.errors:
            return None, self.errors, 400

        kwargs["data"] = self.valid_data
        kwargs["id"] = instance_id
        kwargs["request"] = current_request
        return self.manager.patch(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Delete a resource.

        Args:
            data (dict): Data identifying the resource to delete.
            validate (bool): Whether to validate the data.

        Returns:
            tuple: (instance, error, status_code) - The created instance or validation errors.
                                                   Any error return by serializer is 400
        """
        current_request = CrequestMiddleware.get_request()

        instance_id = kwargs.get("id")
        kwargs["id"] = instance_id
        kwargs["request"] = current_request
        return self.manager.delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        List resources with optional filtering and querying.

        Args:
            id  (int, optional): query for a specific resource
            filter_param (dict, optional): Filters for the listing query.
            query_param (dict, optional): Query parameters for the listing query.

        Returns:
            tuple: (QuerySet, error, status_code) - The created instance or validation errors.
                                                    Any error return by serializer is 400
        """
        instance_id = kwargs.get("id")
        query_params = kwargs.get("query_params")
        current_request = CrequestMiddleware.get_request()
        if query_params:
            self.validate(query_params)
            if self.errors:
                return None, self.errors, 400
        kwargs["request"] = current_request
        return self.manager.get(*args, **kwargs)


class ServiceFactory(CRUDService, response_handler.ResponseHandler):
    """
    Factory class integrating CRUD operations with response handling.
    """

    def __init__(self, manager, serializer=None) -> None:
        super().__init__(manager, serializer)
