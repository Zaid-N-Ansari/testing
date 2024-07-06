# backends.py
from django.contrib.auth.backends import BaseBackend
from .models import UserAccount
from django.db.models import Q

class EmailOrUserIdBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserAccount.objects.get(Q(username=username) | Q(email=username))
        except UserAccount.DoesNotExist:
            return None
        
        if user.check_password(password):
            return user
        return None

    def get_user(self, username):
        try:
            return UserAccount.objects.get(pk=username)
        except UserAccount.DoesNotExist:
            return None
