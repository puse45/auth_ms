from rest_framework_simplejwt.tokens import RefreshToken


class CustomToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        phone_number = getattr(user, "phone_number_model", None)
        email = getattr(user, "email_model", None)
        if email:
            email = email.email
        if phone_number:
            phone_number = phone_number.phone_number
        token = super().for_user(user)
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        token["id"] = str(user.id)
        token["email"] = email
        token["username"] = user.username
        token["is_superuser"] = user.is_superuser
        token["phone_number"] = phone_number
        token["is_active"] = user.is_active
        # You can add more custom data
        return token
