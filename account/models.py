from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.crypto import get_random_string
from ChatApp import settings


class UserAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not username:
            raise ValueError('User must have a Username')
        if not email:
            raise ValueError('User must have an Email Address')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


def get_profile_image_filepath(instance, filename):
    return f'ProfileImage/{instance.pk}/{filename}'


def get_profile_image():
    return f'ChatApp/defaultpfi.jpg'


def generate_unique_username():
    return get_random_string(8)


class UserAccount(AbstractBaseUser):
    id = models.CharField(
            max_length=8,
            primary_key=True,
            default=generate_unique_username
    )

    first_name = models.CharField(
        max_length=10,
        blank=False,
        null=False
    )

    last_name = models.CharField(
        max_length=10,
        blank=False,
        null=False
    )

    username = models.CharField(max_length=30, unique=True)

    email = models.EmailField(
        verbose_name="email",
        max_length=60,
        unique=True
    )
    date_joined = models.DateTimeField(
        verbose_name='date joined',
        auto_now_add=True,
        editable=False
    )
    last_login = models.DateTimeField(
        verbose_name='last login',
        auto_now=True
    )
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    profile_image = models.ImageField(
        max_length=255,
        upload_to=get_profile_image_filepath,
        default=get_profile_image,
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserAccountManager()

    def __str__(self):
        return f'{self.username}'

	
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
    