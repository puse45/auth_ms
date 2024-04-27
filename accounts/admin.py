from django.contrib import admin
from django.contrib.admin.forms import AdminPasswordChangeForm
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from accounts.models import UserPhoneNumberModel, UserEmailModel, User


@admin.register(UserPhoneNumberModel)
class UserPhoneNumberAdminModel(admin.ModelAdmin):
    list_display = [
        "phone_number",
        "user",
        "security_code",
        "is_verified",
        "is_verified",
        "is_password_reset",
        "sent_date",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "is_verified",
        "sent_date",
        "created_at",
        "updated_at",
    ]
    list_display_links = [
        "phone_number",
    ]
    search_fields = [
        "user__id",
        "user__username",
        "security_code",
        "id",
        "phone_number",
    ]
    list_per_page = 50
    save_on_top = True


@admin.register(UserEmailModel)
class UserEmailModelAdminModel(admin.ModelAdmin):
    list_display = [
        "email",
        "user",
        "security_code",
        "is_verified",
        "is_password_reset",
        "sent_date",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "is_verified",
        "sent_date",
        "created_at",
        "updated_at",
    ]
    list_display_links = [
        "email",
    ]
    search_fields = ["user__id", "user__username", "security_code", "id", "email"]
    list_per_page = 50
    save_on_top = True


@admin.register(User)
class UserAdminModel(admin.ModelAdmin):
    add_form_template = "admin/auth/user/add_form.html"
    change_user_password_template = None
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "other_names", "id_number")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    ordering = ("username",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )
    list_display = [
        "username",
        "id_number",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "last_login",
        "date_joined",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "is_staff",
        "is_active",
        "last_login",
        "date_joined",
        "created_at",
        "updated_at",
    ]
    list_display_links = [
        "username",
    ]
    search_fields = ["id", "username"]
    list_per_page = 50
    save_on_top = True
