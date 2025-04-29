from rest_framework import status
from account.business_layer.auth_operation import AuthOperations


class AuthenticationManager:
    """Manages authentication-related database operations and transactions."""

    auth_operation = AuthOperations

    @classmethod
    def post(cls, *args, **kwargs):
        """Handle various authentication-related operations.

        Args:
            data: Dictionary containing request data
            method: String indicating which auth operation to perform

        Returns:
            Tuple of (response_data, error, status_code)
        """
        data = kwargs.get("data", {})
        action = args[0]
        request = kwargs.get("request")
        user = request.user
        if user.is_authenticated:
            data["user"] = user

        # Initialize default values
        error = None
        status_code = None

        # Map of supported methods to their handler functions
        method_handlers = {
            "login": cls.auth_operation.login,
            "register": cls.auth_operation.register,
            "logout": cls.auth_operation.logout,
            "forgot_password": cls.auth_operation.forgot_password,
            "reset_password": cls.auth_operation.reset_password,
            "refresh_token": cls.auth_operation.refresh_token,
            "activate_2fa": cls.auth_operation.activate_2fa,
            "deactivate_2fa": cls.auth_operation.deactivate_2fa,
            "verify_otp": cls.auth_operation.verify_otp,
            "validate_login_otp": cls.auth_operation.validate_login_otp,
            "change_user_password": cls.auth_operation.change_user_password,
        }

        # Get the appropriate handler function
        key = action.replace("-", "_")
        handler = method_handlers.get(key)
        if handler:
            data, error, status_code = handler(data)
        else:
            error = f"Unsupported method: {key}"
            status_code = status.HTTP_400_BAD_REQUEST
            data = None

        return data, error, status_code

    @classmethod
    def get(cls, *args, **kwargs):
        """Retrieve user account(s)."""
        data = kwargs.get("data", {})
        action = args[0]
        request = kwargs.get("request")
        user = request.user
        data["user"] = user

        # Initialize default values
        error = None
        status_code = None

        # Map of supported methods to their handler functions
        method_handlers = {
            "mfa_status": cls.auth_operation.mfa_status,
        }

        # Get the appropriate handler function
        key = action.replace("-", "_")
        handler = method_handlers.get(key)
        if handler:
            data, error, status_code = handler(data)
        else:
            error = f"Unsupported method: {key}"
            status_code = status.HTTP_400_BAD_REQUEST
            data = None

        return data, error, status_code

    @classmethod
    def update(cls, *args, **kwargs):
        """Update user account details."""
        raise NotImplementedError("Method not implement for auth manager")

    @classmethod
    def patch(cls, *args, **kwargs):
        """Partially update user account details."""
        raise NotImplementedError("Method not implement for auth manager")

    @classmethod
    def delete(cls, *args, **kwargs):
        """Delete user account."""
        raise NotImplementedError("Method not implement for auth manager")
