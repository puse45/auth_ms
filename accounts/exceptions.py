from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _


class AccountNotRegisteredException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("The account is not registered.")
    default_code = "non-registered-account"
