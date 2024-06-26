# Generated by Django 4.2.11 on 2024-03-24 22:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_adminprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='street',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.CreateModel(
            name='BusinessProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('businessName', models.CharField(max_length=255)),
                ('businessType', models.CharField(max_length=255)),
                ('businessHours', models.JSONField()),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('contactNo', models.CharField(max_length=50)),
                ('businessLogo', models.CharField(blank=True, max_length=255, null=True)),
                ('websiteUrl', models.CharField(blank=True, max_length=255, null=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
                ('location', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.location')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
