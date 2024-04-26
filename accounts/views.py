import datetime

from django.contrib.auth import authenticate
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.custom_jwt import CustomToken
from accounts.serializers import UserRegistrationSerializer, LoginSerializer, UserSerializer


class UserRegistrationView(views.APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LoginView(views.APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            user.last_login = datetime.datetime.now()
            user.save(update_fields=['last_login'])
            token = CustomToken.for_user(user)
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'refresh': str(refresh),
                    'access': str(token.access_token),
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username,
                }
            )
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


