from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from account.models import UserAccount
from account.views import AsyncLoginRequiredMixin
from asgiref.sync import sync_to_async
from chat.models import ChatRoom, Group
from friend.models import Friend

class IndexChatView(AsyncLoginRequiredMixin, View):
    http_method_names = ['get']
    async def get(self, request, *args, **kwargs):
        my_friends_inst = await Friend.objects.filter(user=request.user).afirst()

        my_friends = await sync_to_async(lambda: my_friends_inst.friends)()

        friends = []

        async for friend in my_friends.aiterator():
            friends.append(friend)

        groups = await sync_to_async(lambda: (Group.objects.filter(participant=request.user)))()

        return await sync_to_async(render)(request, 'chat/chat.html', {
            'friends': friends,
            'groups': groups
        })


class PersonalChatView(AsyncLoginRequiredMixin, View):
    http_method_names = ['post']

    async def post(self, request, *args, **kwargs):
        user_to_connect = request.POST.get('user_or_group_to_connect')

        to_user = await UserAccount.objects.filter(username=user_to_connect).afirst()

        if not to_user:
            return JsonResponse({'error': 'User not found'}, status=404)

        from_user = await UserAccount.objects.aget(username=request.user)

        name = [str(to_user.id), str(from_user.id)]
        name.sort()
        room_name = ''.join(name)

        room, created = await sync_to_async(ChatRoom.objects.get_or_create)(
            room_type=ChatRoom.PERSONAL,
            name=room_name
        )

        return JsonResponse({
            'to': str(to_user),
            'room': room.name
        })


class GroupChatView(AsyncLoginRequiredMixin, View):
    http_method_names = ['post']

    async def post(self, request, *args, **kwargs):
        group_name = request.POST.get('user_or_group_to_connect')

        cr = await ChatRoom.objects.filter(name=group_name).afirst()

        to_group = await Group.objects.filter(chatroom=cr).afirst()

        return JsonResponse({
            'to': str(to_group),
            'room': f'{cr}'
        })

