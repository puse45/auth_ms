# Generated by Django 5.0.4 on 2024-04-27 10:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_alter_user_managers_useremailmodel_is_password_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="useremailmodel",
            old_name="is_password",
            new_name="is_password_reset",
        ),
        migrations.RenameField(
            model_name="userphonenumbermodel",
            old_name="is_password",
            new_name="is_password_reset",
        ),
    ]
