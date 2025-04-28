
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework_simplejwt.exceptions import TokenError
from crequest.middleware import CrequestMiddleware
from account.models import User
from account.models.token import Token
from base.send_email import EmailService
from account.managers.totp import TOTPManager
from account.managers.otp import OTPManager
from base.utils.password_checker import check_password as validate_user_password


class AuthOperations:
    """Handles authentication operations like login, logout, and 2FA."""
    @staticmethod
    def login(data):
        """Authenticate user and return tokens."""
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        request = CrequestMiddleware.get_request()

        if username:
            user = authenticate(username=username, password=password)
        else:
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(request=request, username=user_obj.username, password=password)
                if not user.is_active:
                    return None, "Account is not active", 401
                
                if not user.check_password(password):
                    return None, "Invalid credentials", 401
                
            except User.DoesNotExist:
                return None, "Invalid credentials", 401
            
        if not user:
            return None, "Invalid credentials", 401

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        Token.objects.create(
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
        )
        
        if hasattr(user, 'totp_auth') and user.totp_auth.otp_enabled and user.totp_auth.otp_verified:
            relative_url = reverse('validate-login-otp')
            full_url = request.build_absolute_uri(relative_url)
            return {
                'message': "2FA is enabled. Please use the OTP endpoint to complete authentication.",
                'requires_2fa': True,
                'mfa_url': full_url,
                # 'access_token': access_token,
                'refresh_token': refresh_token,
            }, None, 200
            
        user.last_login = timezone.now()
        user.save()
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'message': "Authentication successful."
        }, None, 200
        
    @staticmethod
    def validate_login_otp(data):
        """Validate OTP token for user authentication.
        
        Args:
            data (dict): Dictionary containing refresh_token and otp
            
        Returns:
            tuple: (data, error, status_code) containing verification result
        """
        refresh_token = data.get('refresh_token')
        otp = data.get('otp')
        
        if not refresh_token or not otp:
            return None, "Refresh token and OTP are required", 400
            
        try:
            
            token = Token.objects.get(refresh_token=refresh_token)
            user = token.user
            
            print(user.totp_auth)
            
            if not hasattr(user, 'totp_auth'):
                return None, "2FA not enabled for this account", 400
            
            data, error, status_code = TOTPManager.verify_totp(otp, user)
                
            if error:
                return None, error, status_code
                
            # If OTP verification successful, return access token
            
            return {
                'access_token': token.access_token,
                'refresh_token': refresh_token,
                'message': "2FA verification successful"
            }, None, 200
            
        except Token.DoesNotExist:
            return None, "Invalid refresh token", 400
        except Exception as e:
            print(e)
            return None, "An error occurred during OTP verification", 500
    

    @staticmethod
    def logout(data):
        """Invalidate user's refresh token."""
        try:
            refresh_token = RefreshToken(data.get('refresh_token'))
            refresh_token.blacklist()
            Token.objects.filter(refresh_token=data.get('refresh_token')).update(is_blacklisted=True)
            
            return {'message': 'Successfully logged out'}, None, 200
        except TokenError:
            return None, "Invalid token", 400

    @staticmethod
    def forgot_password(data):
        """Handle password reset request."""
        try:
            user = User.objects.get(email=data.get('email'))
            # Generate OTP for password reset
            otp_code = OTPManager.generate_otp(user, "Password Reset")
            # Send password reset email with OTP
            EmailService.send_password_reset_email(user, otp_code)
            return {'message': 'Password reset instructions sent to email'}, None, 200
        except ObjectDoesNotExist:
            return None, "User not found", 404

    @staticmethod
    def reset_password(data):
        """Reset user's password."""
        try:
            user = User.objects.get(email=data.get('email'))
            # Verify OTP code
            if not OTPManager.validate_otp(user, data.get('otp')):
                return None, "Invalid or expired OTP code", 400
            user.set_password(data.get('password'))
            user.save()
            return {'message': 'Password successfully reset'}, None, 200
        except ObjectDoesNotExist:
            return None, "User not found", 404
        
    @staticmethod
    def change_user_password(data):
        """Change user's password after verifying old password. If user has totp activated, use their topt token for validation"""
        try:
            request = CrequestMiddleware.get_request()
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            token = data.get('token')
            if request:
                user = request.user
                if hasattr(user, 'totp_auth'):
                    
                    if not token:
                        return None, "OTP is required to change user with MFA activated", status.HTTP_400_BAD_REQUEST
                    
                    data = {"token" : token, "user": user}
                    
                    data, error, status_code = AuthOperations.verify_otp(data) # verify totp token
                    if error:
                        return data, error, status_code
                    
                    data, error = validate_user_password(new_password)
                    if error:
                        return None, error, status.HTTP_406_NOT_ACCEPTABLE
                    
                    user.set_password(new_password) # update new password 
                    user.save()
                    return {'message': 'Password successfully changed'}, None, 200
                else:
                    # Verify old password
                    if not user.check_password(old_password):
                        return None, "Incorrect old password", 400
                    # Set new password
                    user.set_password(new_password) # update new password
                    user.save()
                    return {'message': 'Password successfully changed'}, None, 200
            return {'message': 'No request object detected.'}, None, 400
        except Exception as e:
            return None, str(e), 500


    @staticmethod
    def refresh_token(data):
        """Generate new access token using refresh token."""
        try:
            refresh = RefreshToken(data.get('refresh_token'))
            return {
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'message': "Token refreshed successfully."
            }, None, 200
        except TokenError:
            return None, "Invalid refresh token", 400

    @staticmethod
    def activate_2fa(data):
        """Enable two-factor authentication for user."""
        activate_totp = data.get('activate_totp')
        user = data.get('user')
        data, error, status_code = TOTPManager.activate_totp(activate_totp, user)
        return data, error, status_code

    @staticmethod
    def deactivate_2fa(data):
        """Disable two-factor authentication for user."""
        deactivate_totp = data.get('deactivate_totp')
        user = data.get('user')
        data, error, status_code = TOTPManager.disable_totp(deactivate_totp, user)
        return data, error, status_code
        
    @staticmethod
    def mfa_status(data):
        """Check if OTP is enabled for a user."""
        user = data.get('user')
        data, error, status_code = TOTPManager.mfa_status(user)
        return data, error, status_code
        

    @staticmethod
    def verify_otp(data):
        """Verify OTP token for user."""
        token = data.get('token')
        user = data.get('user')
        data, error, status_code = TOTPManager.verify_totp(token, user)
        return data, error, status_code
    
        