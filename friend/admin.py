from django.contrib import admin
from .models import Friend, FriendRequest, Notification
from asgiref.sync import async_to_sync


class FriendAdmin(admin.ModelAdmin):
    def get_friends_count(self, obj):
        return async_to_sync(obj.friends_count)()

    get_friends_count.short_description = 'Friend Count'.title()

    list_display = ('user', 'get_friends_count')

class FriendRequestAdmin(admin.ModelAdmin):
	list_display = ('from_user', 'to_user')

class NotificationAdmin(admin.ModelAdmin):
	list_display = ('id', 'from_user', 'to_user', 'action', 'seen')

admin.site.register(Friend, FriendAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)
admin.site.register(Notification, NotificationAdmin)