from django.db.models import Q
from django.db import transaction
from rest_framework import status
from account.models import User
from base.send_email import EmailService
from base.utils.password_checker import check_password

class UserBusinessLayer:
    @staticmethod
    def list(kwargs):
        query_params = kwargs.get("query_params")
        error = None
        status_code = status.HTTP_200_OK
        instances = None
        instance_id = kwargs.get("id")
        
        if query_params:
            query_params = dict(kwargs["query_params"])
            # Convert list values to single values since QueryDict returns lists
            query_params = {k: v[0] if isinstance(v, list) else v for k, v in query_params.items()}
        
            search = query_params.get("search")
            
            if search:
                query_params.pop('search')
                # Create an empty Q object to build up the search filters
                filters = Q()
                # Add case-insensitive search filters for each relevant user field
                # This creates an OR condition between all the fields
                # So if search term matches any field, the user will be returned
                filters |= Q(username__icontains=search)
                filters |= Q(email__icontains=search)
                filters |= Q(first_name__icontains=search)
                filters |= Q(last_name__icontains=search)
                query_params = filters
                instances = User.objects.filter(query_params)
                return instances, error, status_code

            instances = User.objects.filter(**query_params)
        elif instance_id:
            instances = UserBusinessLayer.get_user_by_id(instance_id)
            if instances is None:
                error = "User not found"
                status_code = status.HTTP_404_NOT_FOUND
            return instances, error, status_code
        else:
            instances = User.objects.all()
        return instances, error, status_code
    
    @staticmethod
    def get_user_by_id(id):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            return None
        
    @staticmethod
    def create_user(data):
        password = data.pop('password')
        # validate the password follow the standard password requirements 
        is_valid, error = check_password(password)
        if error:
            # if there is an error in the password, return not acceptable status code and the associated error 
            return None, error, status.HTTP_406_NOT_ACCEPTABLE
        
        data['username'] = UserBusinessLayer.generate_username(data.get('first_name'), data.get('last_name'))
        
        instance = User.objects.create(**data)
        if instance:
            instance.set_password(password)
            instance.save()
            EmailService.send_registration_success(instance)
        else:
            return None, "User creation failed", status.HTTP_400_BAD_REQUEST
        return instance, None, status.HTTP_201_CREATED
    
    @staticmethod
    def generate_username(first_name, last_name):
        """
        Generate a username based on first and last name, appending numbers if needed
        """
        # Create base username from first and last name
        base_username = f"{first_name.lower()[0]}{last_name.lower()}"
        username = base_username

        counter = 1
        # Keep checking and incrementing counter until we find an unused username
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        return username
    
    @staticmethod
    def update_user(id, data):
        """Update a user record by id with the provided data.
        
        Args:
            id (int): The id of the user to update
            data (dict): Dictionary containing the fields to update
            
        Returns:
            tuple: (instance, error, status_code)
        """
        instance = UserBusinessLayer.get_user_by_id(id)
        if not instance:
            return None, "User not found", status.HTTP_404_NOT_FOUND
            
        try:
            # Handle password separately if provided
            if 'password' in data:
                password = data.pop('password')
                instance.set_password(password)
            
            # Update other fields
            for key, value in data.items():
                setattr(instance, key, value)
                
            instance.save()
            return instance, None, status.HTTP_200_OK
            
        except Exception as e:
            return None, str(e), status.HTTP_400_BAD_REQUEST
    
    