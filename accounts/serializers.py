from django.conf import settings
from django.contrib.auth import get_user_model
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from accounts.exceptions import AccountNotRegisteredException
from accounts.models import UserPhoneNumberModel, UserEmailModel

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=False, allow_blank=True, source="email_model"
    )
    phone_number = PhoneNumberField(
        required=False, allow_blank=True, source="phone_number_model"
    )

    class Meta:
        model = User
        fields = ["username", "email", "phone_number", "password", "id_number"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        phone_number = validated_data.pop("phone_number_model", None)
        email = validated_data.pop("email_model", None)
        user = User.objects.create_user(
            username=validated_data.pop("username"),
            password=validated_data.pop("password"),
            **validated_data
        )
        if phone_number:
            UserPhoneNumberModel.objects.create(
                user=user, phone_number=phone_number
            ).send_confirmation_code()
        if email:
            UserEmailModel.objects.create(
                user=user, email=email
            ).send_confirmation_code()
        return user

    def validate(self, attrs):
        phone_number = attrs.get("phone_number_model")
        email = attrs.get("email_model")
        if not any([phone_number, email]):
            raise serializers.ValidationError(
                "Please provide either a phone number or an email."
            )
        if (
            phone_number
            and UserPhoneNumberModel.objects.filter(phone_number=phone_number).exists()
        ):
            raise serializers.ValidationError("Phone number already exists.")
        if email and UserEmailModel.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already exists.")
        return attrs


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=False, allow_blank=True, source="email_model"
    )
    phone_number = PhoneNumberField(
        required=False, allow_blank=True, source="phone_number_model"
    )

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "phone_number",
            "email",
            "is_superuser",
            "is_active",
        ]


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=False, allow_blank=True, source="email_model"
    )
    phone_number = PhoneNumberField(
        required=False, allow_blank=True, source="phone_number_model"
    )

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}


class BaseOTP(serializers.Serializer):
    phone_number = PhoneNumberField(allow_null=True, required=False)
    email = serializers.EmailField(allow_null=True, required=False)

    def validate_phone_number(self, value):
        try:
            if UserPhoneNumberModel.objects.get(phone_number=value).is_verified:
                err_message = _("Phone number is verified.")
                raise serializers.ValidationError(err_message)
        except UserPhoneNumberModel.DoesNotExist:
            raise AccountNotRegisteredException()
        return value

    def validate_email(self, value):
        try:
            if UserEmailModel.objects.get(email=value).is_verified:
                err_message = _("Email is verified.")
                raise serializers.ValidationError(err_message)
        except UserEmailModel.DoesNotExist:
            raise AccountNotRegisteredException()
        return value


class GenerateOTPSerializer(BaseOTP):
    class Meta:
        fields = ("phone_number", "email")

    def validate(self, attrs):
        if not any([attrs.get("phone_number"), attrs.get("email")]):
            raise serializers.ValidationError(
                "Please provide either a phone number or an email."
            )
        return attrs

    def create(self, validated_data):
        phone_number = validated_data.get("phone_number")
        email = validated_data.get("email")
        status = True
        if phone_number:
            UserPhoneNumberModel.objects.get(
                phone_number=phone_number
            ).send_confirmation_code()
        if email:
            UserEmailModel.objects.get(email=email).send_confirmation_code()
        return status


class VerifyOTPSerializer(BaseOTP):
    otp = serializers.CharField(
        max_length=settings.TOKEN_LENGTH, required=True, allow_null=False
    )

    class Meta:
        fields = ("phone_number", "email", "otp")

    def create(self, validated_data):
        phone_number = validated_data.get("phone_number")
        email = validated_data.get("email")
        otp = validated_data.get("otp")
        status = False
        if phone_number:
            status = UserPhoneNumberModel.objects.get(
                phone_number=phone_number
            ).check_verification(otp)
        elif email:
            status = UserEmailModel.objects.get(email=email).check_verification(otp)
        return status


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, allow_blank=False)
    password1 = serializers.CharField(required=True, allow_blank=False, min_length=8)
    password2 = serializers.CharField(required=True, allow_blank=False, min_length=8)

    def create(self, validated_data):
        user = self.context["request"].user
        new_password = validated_data.get("password1")
        user.set_password(new_password)
        user.save()
        return True

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("Invalid account password"))
        return value

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def validate(self, attrs):
        pwd1 = attrs.get("password1")
        pwd2 = attrs.get("password2")
        old_password = attrs.get("old_password")
        if pwd1 != pwd2:
            raise serializers.ValidationError(_("Your passwords do not match"))
        if old_password == pwd1:
            raise serializers.ValidationError(
                {
                    "old_password": _(
                        "Your old password cannot be the same as the new password"
                    )
                }
            )
        return attrs


class BasePasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone_number = PhoneNumberField(required=False)

    def validate_phone_number(self, value):
        try:
            if not UserPhoneNumberModel.objects.filter(phone_number=value).exists():
                err_message = _("User with this phone number doesn't exists.")
                raise serializers.ValidationError(err_message)
        except UserPhoneNumberModel.DoesNotExist:
            raise AccountNotRegisteredException()
        return value

    def validate_email(self, value):
        try:
            if not UserEmailModel.objects.filter(email=value).exists():
                err_message = _("User with this email doesn't exists.")
                raise serializers.ValidationError(err_message)
        except UserEmailModel.DoesNotExist:
            raise AccountNotRegisteredException()
        return value


class ResetPasswordSerializer(BasePasswordResetSerializer):
    def create(self, validated_data):
        phone_number = validated_data.get("phone_number")
        email = validated_data.get("email")
        status = True
        if phone_number:
            UserPhoneNumberModel.objects.get(
                phone_number=phone_number
            ).send_confirmation_code(reset_password=True)
        if email:
            UserEmailModel.objects.get(email=email).send_confirmation_code(
                reset_password=True
            )
        return status

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def validate(self, attrs):
        email = attrs.get("email")
        phone_number = attrs.get("phone_number")
        if not any([email, phone_number]):
            raise serializers.ValidationError(_("Email or Phone number is required."))
        return attrs


class PasswordResetConfirmationSerializer(BasePasswordResetSerializer):
    password1 = serializers.CharField(required=True, allow_blank=False, min_length=8)
    password2 = serializers.CharField(required=True, allow_blank=False, min_length=8)
    otp = serializers.CharField(
        max_length=settings.TOKEN_LENGTH, required=True, allow_null=False
    )

    def create(self, validated_data):
        phone_number = validated_data.get("phone_number")
        email = validated_data.get("email")
        otp = validated_data.get("otp")
        password = validated_data.get("password1")
        status = False
        channel = None
        if phone_number:
            channel = UserPhoneNumberModel.objects.get(phone_number=phone_number)
            status = channel.check_verification(otp, reset_password=True)
        elif email:
            channel = UserEmailModel.objects.get(email=email)
            status = channel.check_verification(otp, reset_password=True)
        if status:
            channel.user.set_password(password)
            channel.user.save()
        return status

    def validate(self, attrs):
        pwd1 = attrs.get("password1")
        pwd2 = attrs.get("password2")
        email = attrs.get("email")
        phone_number = attrs.get("phone_number")
        if not any([email, phone_number]):
            raise serializers.ValidationError(_("Email or Phone number is required."))
        if pwd1 != pwd2:
            raise serializers.ValidationError(_("Your passwords do not match"))
        return attrs
