# Generated by Django 4.1.3 on 2024-01-23 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("AdminPanel", "0004_alter_user_roles"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="Roles",
            field=models.ManyToManyField(
                blank=True, null=True, to="AdminPanel.customrole"
            ),
        ),
    ]
