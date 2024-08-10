from django.db import models
from account.models import UserAccount

class ChatRoom(models.Model):
	PERSONAL = 'personal'
	GROUP = 'group'

	ROOM_TYPES = [
		(PERSONAL, 'Personal Chat'),
		(GROUP, 'Group Chat')
	]

	participants = models.ManyToManyField(
		UserAccount
	)

	room_type = models.CharField(
		max_length=12,
		choices=ROOM_TYPES,
		default=PERSONAL
	)

	name = models.CharField(
			max_length=50,
			blank=True,
			null=True
	)

	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.name} | {self.room_type}'


class Message(models.Model):
	chat_room = models.ForeignKey(
		ChatRoom,
		related_name='messages',
		on_delete=models.CASCADE
	)

	from_user = models.ForeignKey(
		UserAccount,
		on_delete=models.CASCADE
	)

	content = models.TextField(max_length=550)

	created_at = models.DateTimeField(auto_now_add=True)

	seen = models.BooleanField(default=False)

	def __str__(self):
		return f'{self.chat_room} | {self.from_user} | {self.content[:10]}'
