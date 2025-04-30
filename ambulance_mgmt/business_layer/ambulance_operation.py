# ambulance/business_layer.py
from django.db.models import Q
from django.db import transaction
from rest_framework import status
from ambulance_mgmt.models import Ambulance


class AmbulanceBusinessLayer:
    @staticmethod
    def list(kwargs):
        """
        List ambulances, optionally filtered by query parameters or retrieve a specific ambulance by ID.

        Args:
            kwargs (dict): Dictionary containing query_params, id, and request.

        Returns:
            tuple: (instances, error, status_code)
                - instances: QuerySet of ambulances or a single ambulance instance.
                - error: Error message if applicable, else None.
                - status_code: HTTP status code.
        """
        query_params = kwargs.get("query_params")
        error = None
        status_code = status.HTTP_200_OK
        instances = None
        instance_id = kwargs.get("id")
        request = kwargs.get("request")

        if query_params:
            query_params = dict(kwargs["query_params"])
            # Convert list values to single values since QueryDict returns lists
            query_params = {
                k: v[0] if isinstance(v, list) else v for k, v in query_params.items()
            }

            search = query_params.get("search")

            if search:
                query_params.pop("search")
                # Create an empty Q object to build up the search filters
                filters = Q()
                # Add case-insensitive search filters for relevant ambulance fields
                filters |= Q(ambulance_id__icontains=search)
                filters |= Q(status__icontains=search)
                filters |= Q(ambulance_type__icontains=search)
                query_params = filters
                instances = Ambulance.objects.filter(query_params)
                return instances, error, status_code
            instances = Ambulance.objects.all()
        elif instance_id:
            instances = AmbulanceBusinessLayer.get_ambulance_by_id(instance_id)
            if instances is None:
                error = "Ambulance not found"
                status_code = status.HTTP_404_NOT_FOUND
            return instances, error, status_code
        else:
            instances = Ambulance.objects.all()
        return instances, error, status_code

    @staticmethod
    def get_ambulance_by_id(id):
        """
        Retrieve an ambulance by its ID.

        Args:
            id (int): The ID of the ambulance.

        Returns:
            Ambulance instance or None if not found.
        """
        try:
            return Ambulance.objects.get(id=id)
        except Ambulance.DoesNotExist:
            return None

    @staticmethod
    def create_ambulance(data):
        """
        Create a new ambulance with the provided data.

        Args:
            data (dict): Dictionary containing ambulance details.

        Returns:
            tuple: (instance, error, status_code)
        """
        # Generate ambulance_id if not provided
        if "ambulance_id" not in data or not data["ambulance_id"]:
            data["ambulance_id"] = AmbulanceBusinessLayer.generate_ambulance_id()

        try:
            with transaction.atomic():
                instance = Ambulance.objects.create(**data)
            return instance, None, status.HTTP_201_CREATED
        except Exception as e:
            return None, str(e), status.HTTP_400_BAD_REQUEST

    @staticmethod
    def generate_ambulance_id():
        """
        Generate a unique ambulance ID (e.g., AMB001, AMB002).

        Returns:
            str: A unique ambulance ID.
        """
        base_id = "AMB"
        counter = 1
        while Ambulance.objects.filter(ambulance_id=f"{base_id}{counter:03d}").exists():
            counter += 1
        return f"{base_id}{counter:03d}"

    @staticmethod
    def update_ambulance(id, data):
        """
        Update an ambulance record by ID with the provided data.

        Args:
            id (int): The ID of the ambulance to update.
            data (dict): Dictionary containing the fields to update.

        Returns:
            tuple: (instance, error, status_code)
        """
        instance = AmbulanceBusinessLayer.get_ambulance_by_id(id)
        if not instance:
            return None, "Ambulance not found", status.HTTP_404_NOT_FOUND

        try:
            with transaction.atomic():
                for key, value in data.items():
                    setattr(instance, key, value)
                instance.save()
            return instance, None, status.HTTP_200_OK
        except Exception as e:
            return None, str(e), status.HTTP_400_BAD_REQUEST

    @staticmethod
    def delete_ambulance(id):
        """
        Delete an ambulance by its ID.

        Args:
            id (int): The ID of the ambulance to delete.

        Returns:
            tuple: (None, error, status_code)
        """
        instance = AmbulanceBusinessLayer.get_ambulance_by_id(id)
        if not instance:
            return None, "Ambulance not found", status.HTTP_404_NOT_FOUND

        try:
            with transaction.atomic():
                instance.delete()
            return None, None, status.HTTP_204_NO_CONTENT
        except Exception as e:
            return None, str(e), status.HTTP_400_BAD_REQUEST
