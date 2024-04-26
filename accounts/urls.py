from django.urls import path, include
from rest_framework.routers import DefaultRouter

from accounts.views import UserRegistrationView, LoginView
from accounts.viewsets import UserViewSet

app_name = "accounts"

router = DefaultRouter()
router.register(r"user", UserViewSet, basename="user")

urlpatterns = []
api_urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("", include(router.urls)),
]
