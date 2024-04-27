from django.urls import path, include
from rest_framework.routers import DefaultRouter

from accounts.views import (
    UserRegistrationView,
    LoginView,
    GenerateOTPView,
    VerifyOTPView,
    ResetPasswordView,
    ResetPasswordConfirmationView,
    PasswordChangeView,
)
from accounts.viewsets import UserViewSet

app_name = "accounts"

router = DefaultRouter()
router.register(r"user", UserViewSet, basename="user")

urlpatterns = []
api_urlpatterns = [
    path("change/password/", PasswordChangeView.as_view(), name="change-password"),
    path("reset/password/", ResetPasswordView.as_view(), name="reset-password"),
    path(
        "reset/password/confirm/",
        ResetPasswordConfirmationView.as_view(),
        name="reset-password-confirmation",
    ),
    path("verify/otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("generate/otp/", GenerateOTPView.as_view(), name="generate-otp"),
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("", include(router.urls)),
]
