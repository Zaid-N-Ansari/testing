from django.contrib import admin
from .models import Friend, FriendRequest

admin.site.register(Friend)

class FriendRequestAdmin(admin.ModelAdmin):
	list_display = ('from_user', 'to_user')
admin.site.register(FriendRequest, FriendRequestAdmin)
