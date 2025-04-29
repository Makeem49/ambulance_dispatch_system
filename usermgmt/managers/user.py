from django.db import transaction
from rest_framework import status
from django.db.models import Q

from base.repository import Repository
from account.models import User
from usermgmt.business_layer.user import UserBusinessLayer

class UserManager(object):
    repository = Repository(User)
    user_business_layer = UserBusinessLayer()
    
    @classmethod
    def post(cls, *args, **kwargs):
        data = kwargs.get('data')
        try:
            with transaction.atomic():
                instance, error, status_code = UserBusinessLayer.create_user(data)
                if error:
                    return None, error, status_code
        except Exception as error:
            return None, str(error), status.HTTP_400_BAD_REQUEST
        return instance, error, status_code
    
    @classmethod
    def get(cls, *args, **kwargs):
        instances, error, status_code = UserBusinessLayer.list(kwargs)
        return instances, error, status_code
    
    @classmethod
    def put(cls, *args, **kwargs):
        data = kwargs.get('data')
        id = kwargs.get('id')
        try:
            with transaction.atomic():
                instance, error, status_code = UserBusinessLayer.update_user(id, data)
                if error:
                    return None, error, status.HTTP_404_NOT_FOUND
        except Exception as error:
            return None, str(error), status.HTTP_400_BAD_REQUEST
        return instance, error, status.HTTP_201_CREATED
    
    @classmethod
    def patch(cls, *args, **kwargs):
        data = kwargs.get('data')
        id = kwargs.get('id')
        try:
            with transaction.atomic():
                instance, error, status_code = UserBusinessLayer.update_user(id, data)
                if error:
                    return None, error, status.HTTP_404_NOT_FOUND
        except Exception as error:
            return None, str(error), status.HTTP_400_BAD_REQUEST
        return instance, error, status.HTTP_201_CREATED
    
    @classmethod
    def delete(cls, *args, **kwargs):
        id = kwargs.get('id')
        filter_param = kwargs.get('filter_param')
        try:
            with transaction.atomic():
                instance, error = cls.repository.delete(id=id, filter_param=filter_param)
                if error:
                    return None, error, status.HTTP_404_NOT_FOUND
        except Exception as error:
            return None, str(error), status.HTTP_400_BAD_REQUEST
        data = {
            'message': 'User deleted successfully'
        }
        return data, None, status.HTTP_200_OK


