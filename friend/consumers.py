import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.utils import timezone as tz
from django.core.paginator import Paginator
from account.models import UserAccount
from .models import Notification
from django.db.models import Q

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        print(f'\n{self.user} connected to notif WS\n')
        if not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = f'{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print(f'\n{self.user} disconnected to notif WS\n')
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')
        print(f'\n{command}\n')
        
        if command == 'mark_seen':
            await self.mark_notifications_seen()
            await self.send(text_data=json.dumps({
				'message': 'notifications_marked_seen',
			}))
        elif command == 'fetch_notifications':
            await self.fetch_notifications(data.get('page', 1), data.get('per_page', 10))

    async def mark_notifications_seen(self):
        # Mark all unseen notifications for the user as seen
        await sync_to_async(Notification.objects.filter(Q(from_user=self.user), seen=False).update)(seen=True)

        print(f'\n{self.user} notif marked at seen \n')

        # Send back confirmation
        await self.send(text_data=json.dumps({
            'status': 'success',
            'message': 'All notifications marked as seen.',
        }))

    async def fetch_notifications(self, page, per_page):
        user = self.user
        user = await UserAccount.objects.aget(username=user)

        unseen_count = await Notification.objects.filter(
            from_user=user, seen=False
        ).acount()

        notifications_qs = await sync_to_async(lambda: Notification.objects.filter(from_user=user).order_by('created_at'))()

        paginator = Paginator(notifications_qs, per_page)
        page = await sync_to_async(lambda: paginator.get_page(page))()
        res:list = []

        async for fr in page.object_list:
            id = await sync_to_async(lambda: fr.id)()
            action = await sync_to_async(lambda: fr.__str__())()
            to_user = await sync_to_async(lambda: fr.to_user)()
            from_user = await sync_to_async(lambda: fr.from_user)()
            created_at = await sync_to_async(lambda: fr.created_at)()
            seen = await sync_to_async(lambda: fr.seen)()
            created_at_local = tz.localtime(created_at)
            natday = naturalday(created_at_local)
            formatted_time = ''
            if natday == 'today':
                formatted_time = f', {naturaltime(created_at_local)}'
            else:
                formatted_time = f' at {created_at_local.strftime("%I:%M %p")}'
            res.append({
                'id': f'{id}',
                'to_user': f'{from_user}',
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
