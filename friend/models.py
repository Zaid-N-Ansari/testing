from django.db import models
from django.conf import settings

class Friend(models.Model):
	user = models.OneToOneField(
			settings.AUTH_USER_MODEL,
			on_delete=models.CASCADE,
			related_name='user'
		)

	friends = models.ManyToManyField(
		settings.AUTH_USER_MODEL,
		blank=True,
		related_name='friend',
	)

	def add_friend(self, user_to_friend):
		if self.user == self.friends.all():
			print("Nahh ahhh..")
		else:
			self.friends.add(user_to_friend)

	def __str__(self):
		return f'{self.user}'
