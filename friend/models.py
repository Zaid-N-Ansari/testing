from django.db import models
from asgiref.sync import sync_to_async
from django.conf import settings
from account.models import UserAccount

class Friend(models.Model):
	user = models.OneToOneField(
			settings.AUTH_USER_MODEL,
			on_delete=models.CASCADE,
			related_name='user',
			unique=True
		)

	friends = models.ManyToManyField(
		UserAccount,
		blank=True,
		related_name='friend',
	)

	def __str__(self):
		return f'{self.user}'

	def is_friend(self, user):
		return self.friends.filter(pk=user.pk).exists()
	
	def add_friend(self, to_add_friend):
		if self.user != to_add_friend:
			self.friends.add(to_add_friend)

	def remove_friend(self, to_remove_friend):
		if self.is_friend(to_remove_friend):
			self.friends.remove(to_remove_friend)

	async def friends_count(self):
		return await self.friends.acount()


class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        UserAccount,
        related_name='req_from_user',
        on_delete=models.CASCADE,
    )
    to_user = models.ForeignKey(
        UserAccount,
        related_name='req_to_user',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def accept(self):
        from_user_friend, _ = Friend.objects.get_or_create(user=self.from_user)
        to_user_friend, _ = Friend.objects.get_or_create(user=self.to_user)

        from_user_friend.add_friend(self.to_user)
        to_user_friend.add_friend(self.from_user)

        Notification.objects.create(
            from_user=self.from_user,
            to_user=self.to_user,
            action=f'Your fr was accepted by {self.to_user}',
            type='regular_notification'
        )

        Notification.objects.create(
            from_user=self.to_user,
            to_user=self.from_user,
            action=f'You accepted fr from {self.from_user}',
            type='regular_notification'
        )
        self.delete()

    def reject(self):
        Notification.objects.create(
            from_user=self.from_user,
            to_user=self.to_user,
            action=f'{self.to_user} rejected your fr',
            type='regular_notification'
        )

        Notification.objects.create(
            from_user=self.to_user,
            to_user=self.from_user,
            action=f'You rejected fr from {self.from_user}',
            type='regular_notification'
        )
        self.delete()


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('friend_request_notification', 'Friend Request Notfication'),
        ('regular_notification', 'Regular Notfication'),
    )

    from_user = models.ForeignKey(
		UserAccount,
		related_name='sent_notifications',
		on_delete=models.CASCADE
	)
    to_user = models.ForeignKey(
		UserAccount,
		related_name='received_notifications',
		on_delete=models.CASCADE
	)
    action = models.CharField(max_length=255)
    type = models.CharField(
		choices=NOTIFICATION_TYPES,
		max_length=30
	)
    created_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
