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
		related_name='friends'
	)

	def __str__(self):
		return f'{self.user.username}'