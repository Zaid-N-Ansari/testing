from django.db import models
from account.models import UserAccount
from asgiref.sync import sync_to_async

class ChatRoom(models.Model):
	PERSONAL = 'personal'
	GROUP = 'group'

	ROOM_TYPES = [
		(PERSONAL, 'Personal Chat'),
		(GROUP, 'Group Chat')
	]

	participants = models.ManyToManyField(UserAccount)

	room_type = models.CharField(
		max_length=12,
		choices=ROOM_TYPES,
		default=PERSONAL
	)

	name = models.CharField(
            max_length=16,
    )

	created_at = models.DateTimeField(auto_now_add=True)

	async def get_participants(self):
		crp = await sync_to_async(lambda: self.participants)()
		return await sync_to_async(lambda: list(crp.all().values_list('username', flat=True)))(), crp

	async def add_user(self, user):
		participants, crp = await self.get_participants()
		if user not in participants:
			await crp.aadd(user)
			return True
		return False

	async def remove_user(self, user):
		participants, crp = await self.get_participants()
		if user in participants:
			await crp.aremove(user)
			return True
		return False

	def __str__(self):
		return f'{self.name}'


class Message(models.Model):
	chat_room = models.ForeignKey(
		ChatRoom,
		on_delete=models.CASCADE
	)

	from_user = models.ForeignKey(
		UserAccount,
		on_delete=models.CASCADE
	)

	content = models.TextField(max_length=550, blank=True, null=True, help_text='message')

	created_at = models.DateTimeField(auto_now_add=True)

	seen = models.BooleanField(default=False)

	def __str__(self):
		return f'{self.chat_room} | {self.from_user} | {self.content[:10]}'
