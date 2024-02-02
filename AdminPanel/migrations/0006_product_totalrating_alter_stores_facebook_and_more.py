# Generated by Django 4.1.3 on 2024-02-02 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("AdminPanel", "0005_alter_user_roles"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="TotalRating",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="stores",
            name="FaceBook",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="stores",
            name="Instagram",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="stores",
            name="Twitter",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="stores",
            name="VideoLink",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]