from django.db import models
from account.models import UserAccount

class Friend(models.Model):
	user = models.OneToOneField(
            UserAccount,
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

	async def is_friend(self, user):
		return await self.friends.filter(pk=user.pk).aexists() and user != self.user

	async def add_friend(self, to_add_friend):
		if await self.is_friend(to_add_friend):
			await self.friends.aadd(to_add_friend)

	async def remove_friend(self, to_remove_friend):
		print(await self.is_friend(to_remove_friend))
		if await self.is_friend(to_remove_friend):
			await self.friends.aremove(to_remove_friend)

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
