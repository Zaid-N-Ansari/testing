from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.utils import timezone as tz
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from typing import Dict
from asgiref.sync import sync_to_async
from django.core.paginator import Paginator
from account.models import UserAccount
from .models import ChatRoom, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            return

        print(f'\n{self.user} connected to chat WS')

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = await UserAccount.objects.filter(username=self.user).afirst()

        self.room = await ChatRoom.objects.filter(name=self.room_name).afirst()

        if await self.room.add_user(self.user):
            await self.accept()

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.broadcast_participants(self.room)

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
                timestamp = tz.localtime(tz.now())
                await Message(
                    chatroom=self.room,
                    from_user=self.user,
                    content=message
                ).asave()
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'send.message',
                        'message': message,
                        'from_user': self.user.username,
                        'timestamp': f'{naturalday(timestamp)} at {timestamp.strftime("%I:%M %p")}'
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
            case 'get_messages':
                await self.get_messages(data.get('page_number', 1), data.get('page_size', 10))

    async def format_notification(self, msg) -> Dict[str, str]:
        created_at = await sync_to_async(lambda: msg.created_at)()
        created_at_local = tz.localtime(created_at)
        timestamp = f'{naturalday(created_at_local)}, {created_at_local.strftime("%I:%M %p")}'
        return {
            'from_user': str(await sync_to_async(lambda: msg.from_user)()),
            'message': str(await sync_to_async(lambda: msg.content)()),
            'created_at': timestamp,
            'seen': str(await sync_to_async(lambda: msg.seen)())
        }

    async def get_messages(self, page, size):
        msgs, total_pages, current_page = await self.fetch_messages(page, size)

        await self.send(text_data=json.dumps({
            'type': 'load_messages',
            'pagination': {
                'current_page': current_page,
                'total_pages': total_pages
            },
            'messages': msgs,
        }))


    async def fetch_messages(self, page, size):
        msg_qs = await sync_to_async(lambda: Message.objects.filter(chatroom=self.room).order_by('-created_at'))()
        paginator = Paginator(msg_qs, size)
        page_obj = await sync_to_async(lambda: paginator.get_page(page))()
        res = []
        async for msg in page_obj.object_list:
            res.append(await self.format_notification(msg))
        return res, paginator.num_pages, page_obj.number

    async def send_message(self, event):
        message = event['message']
        from_user = event['from_user']
        timestamp = event['timestamp']
        await self.send(text_data=json.dumps({
            'type': 'incoming',
            'message': message,
            'from_user': from_user,
            'timestamp': timestamp
        }))

    async def user_typing(self, event):
        from_user = event['from_user']
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'message': 'typing' if self.room.room_type == ChatRoom.PERSONAL else f'{from_user} is typing',
        }))

    async def update_participants(self, event):
        participants = event['participants']
        if len(participants) > 1:
            message = f'{", ".join(participants)} Joined'
        else:
            message = 'Only You are in the Chat Room'

        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'participants': participants,
            'message': message
        }))

    async def disconnect(self, close_code):
        await self.room.remove_user(self.user)
        await self.broadcast_participants(self.room)
        print(f'\n{self.user} disconnected : chat WS')
