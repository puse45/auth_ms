from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import UserPhoneNumberModel, UserEmailModel


@receiver(post_save, sender=UserPhoneNumberModel)
def user_phone_number_model_event(sender, instance, created, **kwargs):
    if not created:
        activate_user(instance, **kwargs)


@receiver(post_save, sender=UserEmailModel)
def user_email_model_event(sender, instance, created, **kwargs):
    if not created:
        activate_user(instance, **kwargs)


def activate_user(instance, **kwargs):
    if instance.is_verified and not instance.user.is_active:
        instance.user.is_active = True
        instance.user.save()
