import random
import datetime
from django.utils import timezone
from account.models import OTP

class OTPManager:
    """Manager class for OTP operations including generation, validation and retrieval."""
    
    @staticmethod
    def generate_otp(user, purpose, expiry_minutes=10):
        """
        Generate a new 6-digit OTP code for a user.
        
        Args:
            user: User object to generate OTP for
            expiry_minutes (int): Minutes until OTP expires
            
        Returns:
            str: Generated OTP code
        """
        # Delete any existing OTP for this user
        OTP.objects.filter(user=user).delete()
        
        # Generate random 6 digit code
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Calculate expiry time
        expires_at = timezone.now() + datetime.timedelta(minutes=expiry_minutes)
        
        # Create and save new OTP
        otp = OTP.objects.create(
            user=user,
            code=code,
            expires_at=expires_at,
            purpose=purpose
        )
        
        return code

    @staticmethod
    def validate_otp(user, code):
        """
        Validate an OTP code for a user.
        
        Args:
            user: User object to validate OTP for
            code (str): OTP code to validate
            
        Returns:
            bool: True if OTP is valid, False otherwise
        """
        try:
            otp = OTP.objects.get(user=user, code=code)
            
            # Check if OTP is still valid
            if otp.is_valid():
                # Delete OTP after successful validation
                otp.delete()
                return True
                
            # Delete expired OTP
            otp.delete()
            return False
            
        except OTP.DoesNotExist:
            return False

    @staticmethod
    def get_valid_otp(user):
        """
        Get valid OTP for a user if one exists.
        
        Args:
            user: User object to get OTP for
            
        Returns:
            OTP: Valid OTP object if exists, None otherwise
        """
        try:
            otp = OTP.objects.get(user=user)
            if otp.is_valid():
                return otp
            
            # Delete expired OTP
            otp.delete()
            return None
            
        except OTP.DoesNotExist:
            return None
