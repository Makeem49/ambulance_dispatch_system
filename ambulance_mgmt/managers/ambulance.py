from django.db import transaction
from rest_framework import status
from base.repository import Repository
from ambulance_mgmt.models.ambulance import Ambulance


class AmbulanceManager(object):
    repository = Repository(Ambulance)

    @classmethod
    def post(cls, *args, **kwargs):
        data = kwargs.get("data")
        request = kwargs.get("request")
        try:
            with transaction.atomic():
                instance, error = cls.repository.create(data=data)
                if error:
                    return None, error, status.HTTP_400_BAD_REQUEST
        except Exception as error:
            return None, str(error), status.HTTP_400_BAD_REQUEST
        return instance, error, status.HTTP_201_CREATED

    @classmethod
    def get(cls, *args, **kwargs):
        filter_param = kwargs.get("query_params")
        id = kwargs.get("id")

        instances, error = cls.repository.list(filter_param=filter_param, id=id)
        return instances, error, status.HTTP_200_OK

    @classmethod
    def put(cls, *args, **kwargs):
        data = kwargs.get("data")
        id = kwargs.get("id")
        try:
            with transaction.atomic():
                instance, error = cls.repository.update(data=data, id=id)
                if error:
                    return None, error, status.HTTP_404_NOT_FOUND
        except Exception as error:
            return None, str(error), status.HTTP_400_BAD_REQUEST
        return instance, error, status.HTTP_201_CREATED

    @classmethod
    def patch(cls, *args, **kwargs):
        data = kwargs.get("data")
        id = kwargs.get("id")
        try:
            with transaction.atomic():
                instance, error = cls.repository.patch(data=data, id=id)
                if error:
                    cls.status_code = 400
                    return None, error, status.HTTP_404_NOT_FOUND
        except Exception as error:
            return None, str(error), status.HTTP_400_BAD_REQUEST
        return instance, error, status.HTTP_200_OK

    @classmethod
    def delete(cls, *args, **kwargs):
        id = kwargs.get("id")
        filter_param = kwargs.get("filter_param")
        try:
            with transaction.atomic():
                instance, error = cls.repository.delete(
                    id=id, filter_param=filter_param
                )
                if error:
                    return None, error, status.HTTP_404_NOT_FOUND
        except Exception as error:
            return None, str(error), status.HTTP_400_BAD_REQUEST
        return instance, None, status.HTTP_200_OK
