from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import ChatRoom, Message
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            return

        print(f'\n{self.user} connected to chat WS')

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        room = await ChatRoom.objects.filter(name=self.room_name).afirst()
        await room.add_user(self.user)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'test_chat_message',
                'message': 'test_new_message',
            }
        )


    async def test_chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(
            {'message': message,}
		))


    async def disconnect(self, close_code):
        room = await ChatRoom.objects.filter(name=self.room_name).afirst()
        await room.remove_user(self.user)
        print(f'\n{self.user} disconnected to chat WS')