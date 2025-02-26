import datetime
import logging
from django.core import signing
from django.shortcuts import redirect
from django.contrib.auth import login
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import views, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.custom_jwt import CustomToken
from accounts.serializers import (
    UserRegistrationSerializer,
    GenerateOTPSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
    PasswordResetConfirmationSerializer,
    PasswordChangeSerializer,
)
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)
oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    access_token_url="https://accounts.google.com/o/oauth2/token",
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    access_token_params=None,
    refresh_token_url=None,
    client_kwargs={"scope": "openid profile email"},
)


def google_login(request):
    metadata = oauth.google.load_server_metadata()
    print(metadata)
    state = signing.dumps({"some_data": "value"})
    request.session["state"] = state  # Store in session
    redirect_uri = f"{settings.SITE_URL}/api/auth/callback/"
    return oauth.google.authorize_redirect(request, redirect_uri, state=state)


def auth_callback(request):
    state = request.GET.get("state")
    if state != request.session.get("state"):
        raise ValueError("Invalid state parameter")
    token = oauth.google.authorize_access_token(request)
    user_info = oauth.google.parse_id_token(request, token)
    logger.warning("User Info:", user_info)
    user = authenticate(request, user_info=user_info)
    if user:
        login(request, user)
        return redirect("/profile")
    return redirect("/")


class UserRegistrationView(views.APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(views.APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            # check if registration channel is verified
            is_phone_number_verified = user.is_phone_number_verified()
            is_email_verified = user.is_email_verified()
            if not any([is_email_verified, is_phone_number_verified]):
                message = "You need to verify your"
                if is_email_verified is False:
                    message += " email."
                elif is_phone_number_verified is False:
                    message += " phone number."
                message += " Kindly generate OTP to verify."
                return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
            user.last_login = datetime.datetime.now()
            user.save(update_fields=["last_login"])
            token = CustomToken.for_user(user)
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(token.access_token),
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                }
            )
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


class GenerateOTPView(GenericAPIView):
    serializer_class = GenerateOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            response = {"message": _("OTP sent.")}
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            message = {"message": _("Successfully verified.")}
            return Response(message, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(
            {"message": "Password changed successful."}, status=status.HTTP_200_OK
        )


class ResetPasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context=self.get_serializer_context()
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"message": "Reset OTP sent."}, status=status.HTTP_200_OK)


class ResetPasswordConfirmationView(GenericAPIView):
    serializer_class = PasswordResetConfirmationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context=self.get_serializer_context()
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(
            {"message": "Password resat successful."}, status=status.HTTP_200_OK
        )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "username": user.username,
                "email": user.email,
            }
        )
