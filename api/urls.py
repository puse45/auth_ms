from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_swagger.views import get_swagger_view
from accounts.urls import api_urlpatterns as accounts_api_url

router = DefaultRouter()

app_name = "api"

schema_view = get_swagger_view(title="API Playground")
urlpatterns = [
    path("swagger/", schema_view, name="swagger"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("", include(accounts_api_url)),
]