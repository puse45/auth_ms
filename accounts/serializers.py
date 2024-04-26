from django.contrib.auth import get_user_model
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from accounts.models import UserPhoneNumberModel, UserEmailModel

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_blank=True,source="email_model")
    phone_number = PhoneNumberField(required=False, allow_blank=True,source="phone_number_model")
    class Meta:
        model = User
        fields = ['username', 'email', "phone_number", 'password',"id_number"]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number_model',None)
        email = validated_data.pop('email_model',None)
        user = User.objects.create_user(
            username=validated_data.pop('username'),
            password=validated_data.pop('password'),
            **validated_data
        )
        if phone_number:
            UserPhoneNumberModel.objects.create(user=user, phone_number=phone_number).send_confirmation()
        if email:
            UserEmailModel.objects.create(user=user, email=email).send_confirmation()
        return user
    def validate(self, attrs):
        phone_number = attrs.get('phone_number_model')
        email = attrs.get('email_model')
        if not any([phone_number, email]):
            raise serializers.ValidationError("Please provide either a phone number or an email.")
        if phone_number and UserPhoneNumberModel.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError("Phone number already exists.")
        if email and UserEmailModel.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already exists.")
        return attrs



class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_blank=True, source="email_model")
    phone_number = PhoneNumberField(required=False, allow_blank=True, source="phone_number_model")

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
    email = serializers.EmailField(required=False, allow_blank=True,source="email_model")
    phone_number = PhoneNumberField(required=False, allow_blank=True,source="phone_number_model")
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {'password': {'write_only': True}}
