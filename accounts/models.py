import logging

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from accounts.managers import UserManager
from accounts.tasks import send_sms_task,send_email_task
from base.models import BaseModel, VerificationModel
from accounts.helpers import generate_security_code

logger = logging.getLogger(__name__)




class User(BaseModel, AbstractUser):
    id_number = models.CharField(max_length=255, null=True)
    other_names = models.CharField(max_length=255, null=True, blank=True)
    email = None

    objects = UserManager()

    EMAIL_FIELD = "username"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]
        get_latest_by = "-first_name"

    def __str__(self):
        return self.username

class UserPhoneNumberModel(BaseModel,VerificationModel):
    user = models.OneToOneField(User, related_name="phone_number_model", on_delete=models.CASCADE)
    phone_number = PhoneNumberField(unique=True)


    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Phone Number")
        verbose_name_plural = _("Phone Numbers")
        get_latest_by = ("-updated_at",)

    def __str__(self):
        return self.phone_number.as_e164


    def send_confirmation(self):
        if not self.is_verified:
            self.security_code = generate_security_code()
            logger.info(f"Sending security code {self.security_code} to phone {self.phone_number}")
            self.sent = timezone.now()
            self.save()

            send_sms_task.delay(str(self.phone_number),
                                    f"Your activation code is {self.security_code}. "
                                    f"It will be active for the next "
                                    f"{settings.TOKEN_EXPIRE_MINUTES} minutes.")

            return self.security_code



class UserEmailModel(BaseModel,VerificationModel):
    user = models.OneToOneField(User, related_name="email_model", on_delete=models.CASCADE)
    email = models.EmailField(unique=True,null=False, blank=False)


    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Email")
        verbose_name_plural = _("Emails")
        get_latest_by = ("-updated_at",)

    def __str__(self):
        return self.email

    def send_confirmation(self):
        if not self.is_verified:
            self.security_code = generate_security_code()
            logger.info(f"Sending security code {self.security_code} to email {self.email}")
            self.save()
            message = f"Your activation code is {self.security_code}.It will be active for the next {settings.TOKEN_EXPIRE_MINUTES} minutes."
            send_email_task.delay(self.email,"Email Confirmation",message)

            return self.security_code



