from itertools import pairwise
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import ChatRoom

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            return

        print(f'\n{self.user} connected to chat WS')

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        room = await ChatRoom.objects.filter(name=self.room_name).afirst()
        if await room.add_user(self.user):
            await self.accept()

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.send_update(room)


    async def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')

        match command:
            case 'send_message':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'send.message',
                        'message': data['message']
                    }
                )


    async def send_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(
            {'message': message,}
		))


    async def send_update(self, room):
        participants, _ = await room.get_participants()
        participants = [_ for _ in participants if _ != self.user.username]
        if len(participants) > 0:
            await self.send(text_data=json.dumps({
                'type': 'status_update',
                'message': f'{participants}'
            }))
        else:
            await self.send(text_data=json.dumps({
                'type': 'status_update',
                'message': 'You are alone in the chat room'
            }))



    async def disconnect(self, close_code):
        room = await ChatRoom.objects.filter(name=self.room_name).afirst()
        await room.remove_user(self.user)
        await self.send_update(room)
        print(f'\n{self.user} disconnected : chat WS')