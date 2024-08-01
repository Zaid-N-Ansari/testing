from django.db import models
from django.conf import settings

class Friend(models.Model):
	user = models.OneToOneField(
			settings.AUTH_USER_MODEL,
			on_delete=models.CASCADE,
			related_name='user',
			unique=True
		)

	friends = models.ManyToManyField(
		settings.AUTH_USER_MODEL,
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


class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='req_from_user',
        on_delete=models.CASCADE,
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='req_to_user',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def accept(self):
        # Get or create Friend objects for both users and add them as friends
        from_user_friend, created = Friend.objects.get_or_create(user=self.from_user)
        to_user_friend, created = Friend.objects.get_or_create(user=self.to_user)
        
        from_user_friend.add_friend(self.to_user)
        to_user_friend.add_friend(self.from_user)

        # Create notifications for both users
        Notification.objects.create(
            from_user=self.from_user,
            to_user=self.to_user,
            action='accepted_friend_request'
        )
        
        Notification.objects.create(
            from_user=self.to_user,
            to_user=self.from_user,
            action='accepted_friend_request'
        )

        # Delete the friend request after acceptance
        self.delete()

    def reject(self):
        # Create notifications for both users indicating rejection
        Notification.objects.create(
            from_user=self.from_user,
            to_user=self.to_user,
            action='rejected_friend_request'
        )
        
        Notification.objects.create(
            from_user=self.to_user,
            to_user=self.from_user,
            action='rejected_friend_request'
        )

        # Delete the friend request after rejection
        self.delete()


class Notification(models.Model):
	ACTION_CHOICES = [
        ('sent_friend_request', 'Sent Friend Request to'),
        ('received_friend_request', 'Received Friend Request from'),
        ('accepted_friend_request', 'Accepted Friend Request'),
        ('rejected_friend_request', 'Rejected Friend Request'),
        ('unfriended', 'Unfriended'),
    ]

	from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notifications_sent',
        on_delete=models.CASCADE,
    )
	to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notifications_received',
        on_delete=models.CASCADE,
    )
	action = models.CharField(max_length=50, choices=ACTION_CHOICES)
	created_at = models.DateTimeField(auto_now_add=True)
	seen = models.BooleanField(default=False)

	def __str__(self):
		return f'You {self.get_action_display()} {self.to_user}'

	def mark_as_seen(self):
		self.seen = True
		self.save()