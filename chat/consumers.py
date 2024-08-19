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

        await self.broadcast_participants(room)

    async def broadcast_participants(self, room):
        participants, _ = await room.get_participants()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'update.participants',
                'participants': participants
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')

        match command:
            case 'send_message':
                message = data.get('message')
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'send.message',
                        'message': message,
                        'from_user': self.user.username
                    }
                )
            case 'typing':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user.typing',
                        'from_user': self.user.username
                    }
                )


    async def send_message(self, event):
        message = event['message']
        from_user = event['from_user']
        await self.send(text_data=json.dumps({
            'type': 'incoming',
            'message': message,
            'from_user': from_user
        }))

    async def user_typing(self, event):
        from_user = event['from_user']
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'from_user': from_user
        }))

    async def update_participants(self, event):
        participants = event['participants']
        if len(participants) > 1:
            message = f'{', '.join(participants)} Joined'
        else:
            message = 'Only You are in the Chat Room'

        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'participants': participants,
            'message': message
        }))

    async def disconnect(self, close_code):
        room = await ChatRoom.objects.filter(name=self.room_name).afirst()
        await room.remove_user(self.user)
        await self.broadcast_participants(room)
        print(f'\n{self.user} disconnected : chat WS')
