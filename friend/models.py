from typing import AsyncIterator
from django.db import models
from django.conf import settings
from django.db.models import QuerySet

from account.models import UserAccount

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
					related_query_name='from_user',
				)
	to_user = models.ForeignKey(
					settings.AUTH_USER_MODEL,
					related_name='req_to_user',
					on_delete=models.CASCADE,
					related_query_name='to_user',
				)
	created_at = models.DateTimeField(auto_created=True, auto_now_add=True)

	def __str__(self):
		return f'You sent a friend request to {self.to_user}'

	def accept(self):
		Friend.objects.get_or_create(user=self.from_user).add_friend(self.to_user)
		Friend.objects.get_or_create(user=self.to_user).add_friend(self.from_user)

	def reject(self):
		self.delete()