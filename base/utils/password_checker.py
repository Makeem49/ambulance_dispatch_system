from rest_framework import serializers
from base.constants.password import COMMON_PASSWORDS


def check_password(value):
    """Check if the password is valid."""
    errors = []
    data = True
    if len(value) < 12:
        errors.append("Password must be at least 12 characters long")
        data = False

    # Check for uppercase letters
    if not any(c.isupper() for c in value):
        errors.append("Password must contain at least one uppercase letter")
        data = False
    # Check for lowercase letters
    if not any(c.islower() for c in value):
        errors.append("Password must contain at least one lowercase letter")
        data = False
    # Check for numbers
    if not any(c.isdigit() for c in value):
        errors.append("Password must contain at least one number")
        data = False
    # Check for special characters
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in value):
        errors.append("Password must contain at least one special character")
        data = False
    # Check for common patterns

    if any(pattern in value.lower() for pattern in COMMON_PASSWORDS):
        errors.append("Password contains common patterns that are not allowed")
        data = False

    return data, errors
