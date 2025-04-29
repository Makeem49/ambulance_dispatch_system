from django.urls import path

from usermgmt.views import user

urlpatterns = [
    path("", user.UserAPIView.as_view(), name="users"),
    path("<int:id>", user.UserAPIView.as_view(), name="user"),
]
