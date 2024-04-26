from rest_framework import mixins, viewsets
from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated

from accounts.serializers import UserSerializer

User = get_user_model()
class UserViewSet(mixins.ListModelMixin,
                mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset.all()
        return self.queryset.filter(id=self.request.user.id)




