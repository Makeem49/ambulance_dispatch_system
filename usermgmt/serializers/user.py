from rest_framework import serializers
from account.models import User
from base.utils.password_checker import check_password

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'first_name', 'last_name', 'role']
        
    def validate_password(self, value):
        check_password(value)
        return value
        
class UserSearchAndFilterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255)
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    role = serializers.CharField(max_length=255)
    is_active = serializers.BooleanField(default=True)
    is_staff = serializers.BooleanField(default=False)
    is_2fa_enabled = serializers.BooleanField(default=True)
    is_email_verified = serializers.BooleanField(default=False)
    search = serializers.CharField(max_length=255)
    
    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].required = False
    

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'is_2fa_enabled', 'is_email_verified', 'created', 'updated']
        
class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'created']

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username',
                  'email', 
                  'first_name',
                  'last_name', 
                  'role', 
                  'is_active', 
                  'is_staff', 
                  'is_2fa_enabled', 
                  'is_email_verified', 
                  'bio', 
                  'website',
                  'reading_preferences',    
                  ]

class UserPartialUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        
    def __init__(self, instance=None, data=..., **kwargs):
        print('hello')
        super().__init__(instance, data, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].required = False

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']
        
        
class DeleteUserSerializer(serializers.Serializer):
    message = serializers.CharField()
