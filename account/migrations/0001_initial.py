# Generated by Django 5.0.6 on 2024-07-07 06:42

import account.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserAccount',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('id', models.CharField(default=account.models.generate_unique_username, editable=False, max_length=8, primary_key=True, serialize=False)),
                ('username', models.CharField(editable=False, max_length=30, unique=True)),
                ('email', models.EmailField(max_length=60, unique=True, verbose_name='email')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('last_login', models.DateTimeField(auto_now=True, verbose_name='last login')),
                ('is_admin', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('profile_image', models.ImageField(blank=True, default=account.models.get_profile_image, max_length=255, null=True, upload_to=account.models.get_profile_image_filepath)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
