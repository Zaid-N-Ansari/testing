import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.utils import timezone as tz
from django.core.paginator import Paginator
from account.models import UserAccount
from .models import FriendRequest, Notification
from typing import List, Dict

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


    async def format_notification(self, notif) -> Dict[str, str]:
        created_at = await sync_to_async(lambda: notif.created_at)()
        created_at_local = tz.localtime(created_at)
        natday = naturalday(created_at_local)
        formatted_time = f', {naturaltime(created_at_local)}' if natday == 'today' else f' at {created_at_local.strftime("%I:%M %p")}'
        return {
            'id': str(await sync_to_async(lambda: notif.id)()),
            'type': str(await sync_to_async(lambda: notif.type)()),
            'from_user': str(await sync_to_async(lambda: notif.to_user)()),
            'created_at': f'{natday}{formatted_time}',
            'action': str(await sync_to_async(lambda: notif.action)()),
            'count': str(await Notification.objects.filter(from_user=(await sync_to_async(lambda: notif.from_user)()), seen=False).acount()),
            'seen': str(await sync_to_async(lambda: notif.seen)())
        }


    async def get_notifications(self, user, page, per_page) -> List[Dict[str, str]]:
        notif_qs = await sync_to_async(lambda: Notification.objects.filter(from_user=user).order_by('-created_at'))()
        paginator = Paginator(notif_qs, per_page)
        page_obj = await sync_to_async(lambda: paginator.get_page(page))()
        res = []
        async for notif in page_obj.object_list:
            res.append(await self.format_notification(notif))
        return res, paginator.num_pages, page_obj.number


    async def handle_friend_request(self, to_be_friend, id, action):
        to_be_friend = await UserAccount.objects.filter(username=to_be_friend).afirst()
        fr = await FriendRequest.objects.filter(from_user=to_be_friend).afirst()
        notif = await Notification.objects.filter(id=id).afirst()

        notif.type = 'regular_notification'
        await notif.asave()

        if action == 'accept':
            await sync_to_async(fr.accept)()
        elif action == 'reject':
            await sync_to_async(fr.reject)()

        notification = await self.format_notification(notif)

        await self.send(text_data=json.dumps({
            'status': 'success',
            'notification': notification,
        }))
        print(f'{to_be_friend} {action}ed your fr')


    async def accept_fr(self, to_be_friend, id):
        await self.handle_friend_request(to_be_friend, id, 'accept')


    async def reject_fr(self, to_be_friend, id):
        await self.handle_friend_request(to_be_friend, id, 'reject')


    async def fetch_notifications(self, page, per_page):
        user = self.user

        notifications, total_pages, current_page = await self.get_notifications(user, page, per_page)

        await self.send(text_data=json.dumps({
            'notifications': notifications,
            'pagination': {
                'total_pages': total_pages,
                'current_page': current_page
            }
        }))

    async def mark_notifications_seen(self, id):
        await sync_to_async(Notification.objects.filter(from_user=self.user, seen=False, id=id).update)(seen=True)

        print(f'Notification with id-{id} marked Seen\n')

        await self.send(text_data=json.dumps({
            'status': 'success',
            'message': f'Notification with id-{id} marked Seen',
        }))