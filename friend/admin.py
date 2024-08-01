from django.contrib import admin
from .models import Friend, FriendRequest, Notification

class FriendRequestAdmin(admin.ModelAdmin):
	list_display = ('from_user', 'to_user')

class NotificationAdmin(admin.ModelAdmin):
	list_display = ('from_user', 'to_user', 'action')

admin.site.register(Friend)
admin.site.register(FriendRequest, FriendRequestAdmin)
admin.site.register(Notification, NotificationAdmin)