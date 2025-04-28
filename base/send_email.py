from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task


class EmailService:
    """Service class for sending emails to users."""

    @staticmethod
    def send_email(to_email, subject, message, html_message=None):
        """
        Send an email to a user.

        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            message (str): Plain text message content
            html_message (str, optional): HTML formatted message content

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            # Log the error here if needed
            return False

    @staticmethod
    def send_password_reset_email(user, otp_code):
        """
        Send password reset email to user.

        Args:
            user: User object containing email
            reset_link (str): Password reset link

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        subject = "Password Reset Request"
        message = f"""
        Hello {user.username},
        
        You recently requested to reset your password. Use the one time otp code below to reset it:
        
        {otp_code}
        
        If you did not request this reset, please ignore this email.
        
        Thanks,
        The Team
        """

        return EmailService.send_email(user.email, subject, message)

    @staticmethod
    @shared_task
    def send_email_async(to_email, subject, message, html_message=None):
        """
        Celery task to send email asynchronously.

        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            message (str): Plain text message content
            html_message (str, optional): HTML formatted message content

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            # Log the error here if needed
            return False

    @staticmethod
    def send_2fa_code(user, code):
        """
        Send 2FA verification code email.

        Args:
            user: User object containing email
            code (str): 2FA verification code

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        subject = "Two-Factor Authentication Code"
        message = f"""
        Hello {user.username},
        
        Your verification code is: {code}
        
        This code will expire in 10 minutes.
        
        Thanks,
        The Team
        """

        return EmailService.send_email_async(user.email, subject, message)

    @staticmethod
    def send_registration_success(user):
        """
        Send registration success email.

        Args:
            user: User object containing email and username

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        subject = "Welcome to Our Platform!"
        message = f"""
        Hello {user.username},
        
        Thank you for registering on our platform! We're excited to have you join our community.
        
        Your account has been successfully created. You can now:
        - Browse and purchase books
        - Create and publish your own books (if you're an author)
        - Manage your profile and preferences
        
        If you have any questions or need assistance, please don't hesitate to contact our support team.
        
        Happy reading!
        
        Best regards,
        The Team
        """

        return EmailService.send_email_async(user.email, subject, message)
