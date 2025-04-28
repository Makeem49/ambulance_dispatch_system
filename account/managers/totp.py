import pyotp
from django.db import transaction
from rest_framework import status
from django.conf import settings
from account.models import TOTPAuth

TOTP_ISSUER_NAME = getattr(settings, "TOTP_ISSUER_NAME", "drftotp")

class TOTPManager:
    """Manager class for OTP operations including generation, validation and retrieval."""
    
    @staticmethod
    def activate_totp(activate_totp, user):
        """Activate TOTP for user authentication.
        
        Args:
            activate_totp (bool): Flag to activate TOTP
            user (User): User object to activate TOTP for
            
        Returns:
            tuple: (data, error, status_code) containing activation result
        """
        error = data = None
        if activate_totp:
            try:
                with transaction.atomic():
                    # user = request.user
                    auth, created = TOTPAuth.objects.get_or_create(user=user)

                    if auth.otp_verified:
                        error = "TOTP already enabled and verified."
                        return None, error, status.HTTP_400_BAD_REQUEST

                    totp = pyotp.random_base32()
                    auth.otp_base32 = totp

                    provisioning_uri = pyotp.totp.TOTP(totp).provisioning_uri(
                        name=user.email, issuer_name=TOTP_ISSUER_NAME
                    )
                    auth.otp_auth_url = provisioning_uri
                    verified = auth.otp_verified
                    auth.save()
                    data = {"message": "TOTP activated successfully.", "otp_auth_url": provisioning_uri, "verified": verified}
                    return data, error, status.HTTP_200_OK
            except Exception as e:
                print(e)
                error =  "TOTP activation failed."
                return None, error, status.HTTP_400_BAD_REQUEST
        else:
            error =  "TOTP activation failed."
            return None, error, status.HTTP_400_BAD_REQUEST
        
    @staticmethod
    def verify_totp(token, user):
        """Verify TOTP token for user authentication.
        
        Args:
            token (str): The TOTP token to verify
            user (User): The user object to verify token against
            
        Returns:
            tuple: (data, error, status_code) containing verification result
        """
        error = data = None
        try:
            auth = TOTPAuth.objects.get(user=user)

            if not auth.otp_base32:
                error = "TOTP not enabled."
                return None, error, status.HTTP_400_BAD_REQUEST

            totp = pyotp.TOTP(auth.otp_base32)
            print(totp.now())
            if totp.verify(token):
                auth.otp_verified = True
                auth.otp_enabled = True
                auth.save()
                data = {"message": "TOTP verified successfully", "verified": auth.otp_enabled }
                return data, error, status.HTTP_200_OK

            error = "Invalid token"
            return None, error, status.HTTP_400_BAD_REQUEST

        except TOTPAuth.DoesNotExist:
            error = "TOTP auth not found. Please generate TOTP first."
            return None, error, status.HTTP_400_BAD_REQUEST
        except Exception as e:
            print(e)
            error = "An error occurred while verifying TOTP."
            return None, error, status.HTTP_500_INTERNAL_SERVER_ERROR
        
    @staticmethod
    def mfa_status(user):
        """Check the status of TOTP for a user.
        
        Args:
            user (User): The user object to check TOTP status for
            
        Returns:
            tuple: (data, error, status_code) containing TOTP status information
        """
        error = data = None
        try:
            auth, _ = TOTPAuth.objects.get_or_create(user=user) # create if not exists

            data = {
                "message": "TOTP enabled." if auth.otp_enabled else "TOTP disabled.",
                "verified": auth.otp_verified,
                "otp_auth_url": auth.otp_auth_url,
            }
            return data, error, status.HTTP_200_OK
        except Exception as e:
            print(e)
            error = "An error occurred while checking TOTP status."
            return None, error, status.HTTP_500_INTERNAL_SERVER_ERROR
        
    @staticmethod
    def disable_totp(deactivate_totp, user):
        """Disable TOTP authentication for a user.
        
        Args:
            deactivate_totp (bool): Flag indicating whether to deactivate TOTP
            user (User): The user object to disable TOTP for
            
        Returns:
            tuple: (data, error, status_code) containing the result of the operation
        """
        error = data = None
        
        if deactivate_totp:
            try:
                with transaction.atomic():
                    auth = TOTPAuth.objects.get(user=user)
                    auth.otp_enabled = False
                    auth.otp_verified = False
                    auth.otp_base32 = None
                    auth.otp_auth_url = None
                    auth.delete()
                data = {"message": "TOTP disabled successfully"}
                return data, error, status.HTTP_200_OK
            except TOTPAuth.DoesNotExist:
                error = "TOTP auth not found"
                return None, error, status.HTTP_400_BAD_REQUEST
        else:
            error = "TOTP deactivation failed."
            return None, error, status.HTTP_400_BAD_REQUEST
