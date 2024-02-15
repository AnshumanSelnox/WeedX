# Generated by Django 4.1.3 on 2024-02-13 10:13

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Employee",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("FirstName", models.CharField(max_length=5000)),
                ("LastName", models.CharField(max_length=5000)),
                ("DOB", models.DateField()),
                ("Study", models.CharField(max_length=20)),
                ("StartDate", models.DateField()),
                ("EndDate", models.DateField()),
                ("CurrentSalary", models.IntegerField()),
                ("Description", ckeditor.fields.RichTextField()),
            ],
        ),
    ]