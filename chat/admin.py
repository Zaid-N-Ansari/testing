from django.contrib import admin
from .models import ChatRoom, Message, Group

admin.site.register(ChatRoom)
admin.site.register(Message)
admin.site.register(Group)