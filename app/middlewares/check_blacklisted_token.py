import jwt
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.conf import settings
from base.response_handler import ResponseHandler
from account.models.token import Token

def is_token_blacklisted(token):
    """Check if the access token is still valid."""
    is_token_exist = Token.objects.filter(access_token=token).first()
    if is_token_exist:
        return is_token_exist.is_blacklisted
    return None 


class CheckBlacklistedTokenMiddleware:
    """
    Middleware to check if the provided JWT refresh token is blacklisted.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            response = None
            try:
                # Extract the token (e.g., "Bearer <token>")
                token = auth_header.split(" ")[1]
                try:    
                    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                    
                    is_token_exist = is_token_blacklisted(token)
                    if is_token_exist:
                        response = ResponseHandler.error(
                            errors="This token has been invalidated due to a user logout. Please login again to get a new token.",
                            message="Token no longer valid",
                            status_code=status.HTTP_401_UNAUTHORIZED
                        )
                    
                except jwt.ExpiredSignatureError:
                    response = ResponseHandler.error(
                        errors="Your authentication token has expired. Please login again to get a new token.",
                        message="Token has expired",
                        status_code=status.HTTP_401_UNAUTHORIZED
                    )
                except jwt.InvalidTokenError:
                    response = ResponseHandler.error(
                        errors="The provided authentication token is invalid or malformed. Please ensure you are using a valid token.",
                        message="Invalid authentication token",
                        status_code=status.HTTP_401_UNAUTHORIZED
                    )
                except Exception as e:
                    response = ResponseHandler.error(errors=str(e), message=str(e), status_code=status.HTTP_401_UNAUTHORIZED)
            
                    
            except IndexError:
                # Handle missing token
                response = ResponseHandler.error(message="Authorization token not provided.", status_code=status.HTTP_400_BAD_REQUEST)

            if response:
                response.accepted_renderer = JSONRenderer()
                response.accepted_media_type = "application/json"
                response.renderer_context = {}
                response.render()
                return response
        # Proceed with the request if the token is not blacklisted
        response = self.get_response(request)
        return response
