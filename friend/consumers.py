import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.utils import timezone as tz
from django.core.paginator import Paginator
from account.models import UserAccount
from .models import FriendRequest, Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        print(f'\n{self.user} connected to notif WS')
        if not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = f'{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print(f'{self.user} disconnected to notif WS\n')
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')
        print(f'{command}\n')

        match command:
            case 'mark_seen':
                id = data.get('id')
                await self.mark_notifications_seen(id)
            case 'fetch_notifications':
                await self.fetch_notifications(data.get('page', 1), data.get('per_page', 10))
            case 'accept_fr':
                to_be_friend = data.get('user')
                id = data.get('id')
                await self.accept_fr(to_be_friend, id)
            case 'reject_fr':
                to_be_friend = data.get('user')
                id = data.get('id')
                await self.reject_fr(to_be_friend, id)

    async def accept_fr(self, to_be_friend, id):
        to_be_friend = await UserAccount.objects.filter(username=to_be_friend).afirst()
        fr = await FriendRequest.objects.filter(from_user=to_be_friend).afirst()
        notif = await Notification.objects.filter(id=id).afirst()
        print(notif)
        notif.type = 'regular_notification'
        await sync_to_async(notif.save)()
        await sync_to_async(fr.accept)()
        await self.send(text_data=json.dumps({
            'status': 'success',
            'message': 'accepted'
        }))
        print(f'{to_be_friend} accepted your fr')

    async def reject_fr(self, to_be_friend, id):
        to_be_friend = await UserAccount.objects.filter(username=to_be_friend).afirst()
        fr = await FriendRequest.objects.filter(from_user=to_be_friend).afirst()
        notif = await Notification.objects.filter(id=id).afirst()
        notif.type = 'regular_notification'
        await sync_to_async(notif.save)()
        await sync_to_async(fr.reject)()
        await self.send(text_data=json.dumps({
            'status': 'success',
            'message': 'rejected'
        }))
        print(f'{to_be_friend} rejected your fr')

    async def mark_notifications_seen(self, id):
        await sync_to_async(Notification.objects.filter(from_user=self.user, seen=False, id=id).update)(seen=True)

        print(f'Notification with id-{id} marked Seen\n')

        await self.send(text_data=json.dumps({
            'status': 'success',
            'message': f'Notification with id-{id} marked Seen',
        }))

    async def fetch_notifications(self, page, per_page):
        user = self.user

        unseen_count = await Notification.objects.filter(from_user=user, seen=False).acount()

        notif_qs = await sync_to_async(lambda: Notification.objects.filter(from_user=user).order_by('-created_at'))()

        paginator = Paginator(notif_qs, per_page)
        page = await sync_to_async(lambda: paginator.get_page(page))()
        res:list = []

        async for notif in page.object_list:
            id = await sync_to_async(lambda: notif.id)()
            type = await sync_to_async(lambda: notif.type)()
            action = await sync_to_async(lambda: notif.action)()
            to_user = await sync_to_async(lambda: notif.to_user)()
            created_at = await sync_to_async(lambda: notif.created_at)()
            seen = await sync_to_async(lambda: notif.seen)()
            created_at_local = tz.localtime(created_at)
            natday = naturalday(created_at_local)
            formatted_time = ''
            if natday == 'today':
                formatted_time = f', {naturaltime(created_at_local)}'
            else:
                formatted_time = f' at {created_at_local.strftime("%I:%M %p")}'
            res.append({
                'id': f'{id}',
                'type': f'{type}',
                'from_user': f'{to_user}',
                'created_at': f'{natday}{formatted_time}',
                'action': f'{action}',
                'count': f'{unseen_count}',
                'seen': f'{seen}'
            })

        pagination = {
            'total_pages': paginator.num_pages,
            'current_page': page.number
        }

        await self.send(text_data=json.dumps({
            'notifications': res,
            'pagination': pagination
        }))
