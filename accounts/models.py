import logging
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from accounts.managers import UserManager
from accounts.tasks import send_sms_task, send_email_task
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

    def is_email_verified(self):
        if hasattr(self, "email_model"):
            return self.email_model.is_verified

    def is_phone_number_verified(self):
        if hasattr(self, "phone_number_model"):
            return self.phone_number_model.is_verified


class UserPhoneNumberModel(BaseModel, VerificationModel):
    user = models.OneToOneField(
        User, related_name="phone_number_model", on_delete=models.CASCADE
    )
    phone_number = PhoneNumberField(unique=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Phone Number")
        verbose_name_plural = _("Phone Numbers")
        get_latest_by = ("-updated_at",)

    def __str__(self):
        return self.phone_number.as_e164

    def send_confirmation_code(self, reset_password=False):
        if not self.is_verified or reset_password:
            self.security_code = generate_security_code()
            logger.info(
                f"Sending security code {self.security_code} to phone {self.phone_number}"
            )
            self.sent_date = timezone.now()
            if reset_password:
                self.is_password_reset = reset_password
            self.save()
            if reset_password:
                message = "Your reset password code is"
            else:
                message = "Your activation code is"
            message += (
                f" {self.security_code}. It will be active "
                f"for the next {settings.TOKEN_EXPIRE_MINUTES} minutes."
            )
            send_sms_task.delay(str(self.phone_number), message)
            return self.security_code


class UserEmailModel(BaseModel, VerificationModel):
    user = models.OneToOneField(
        User, related_name="email_model", on_delete=models.CASCADE
    )
    email = models.EmailField(unique=True, null=False, blank=False)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Email")
        verbose_name_plural = _("Emails")
        get_latest_by = ("-updated_at",)

    def __str__(self):
        return self.email

    def send_confirmation_code(self, reset_password=False):
        if not self.is_verified or reset_password:
            self.security_code = generate_security_code()
            logger.info(
                f"Sending security code {self.security_code} to email {self.email}"
            )
            self.sent_date = timezone.now()
            if reset_password:
                self.is_password_reset = reset_password
            self.save()
            if reset_password:
                message = "Your reset password code is"
                subject = "Reset Password"
            else:
                message = "Your activation code is"
                subject = "Email Confirmation"
            message += (
                f" {self.security_code}. It will "
                f"be active for the next {settings.TOKEN_EXPIRE_MINUTES} minutes."
            )
            send_email_task.delay(self.email, subject, message)

            return self.security_code
