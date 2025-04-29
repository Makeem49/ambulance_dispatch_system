from django.urls import path

from usermgmt.views import user

urlpatterns = [
    path("users", user.UserAPIView.as_view(), name='users'),
    path("users/<int:id>", user.UserAPIView.as_view(), name='user')
]
