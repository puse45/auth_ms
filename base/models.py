import datetime
import logging
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from timestampedmodel import TimestampedModel
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import NotAcceptable

from base.managers import BaseManager


logger = logging.getLogger(__name__)


class BaseModel(TimestampedModel):
    id = models.UUIDField(
        primary_key=True, editable=False, default=uuid.uuid4, db_index=True
    )
    is_archived = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, null=True, blank=True)

    objects = BaseManager()

    class Meta:
        abstract = True
        ordering = ("-updated_at", "-created_at")
        get_latest_by = ("updated_at",)


class VerificationModel(models.Model):
    security_code = models.CharField(max_length=20)
    is_verified = models.BooleanField(default=False)
    is_password_reset = models.BooleanField(default=False)
    sent_date = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    class Meta:
        abstract = True

    def is_security_code_expired(self):
        try:
            expiration_date = self.sent_date + datetime.timedelta(
                minutes=settings.TOKEN_EXPIRE_MINUTES
            )
            return expiration_date <= timezone.now()
        except TypeError as e:
            logger.error(f"Sent, date is not set {e}")
            return False

    def send_confirmation_code(self):
        ...

    def check_verification(self, security_code, reset_password=False):
        if (
            not self.is_security_code_expired()
            and security_code == self.security_code
            and (not self.is_verified or all([reset_password, self.is_password_reset]))
        ):
            self.is_verified = True
            if reset_password:
                self.is_password_reset = False
            self.save()
        else:
            raise NotAcceptable(
                _(
                    "Your OTP is wrong or expired or "
                    "this email is verified or "
                    "password password has been reset."
                )
            )
        return self.is_verified


class ModelOptions:
    @classmethod
    def options(cls):
        return [_ for _ in cls.__dict__.values() if isinstance(_, str)][1:]
