from django.shortcuts import render
from django.views import View
from account.models import UserAccount
from account.views import AsyncLoginRequiredMixin
from asgiref.sync import sync_to_async
from chat.models import ChatRoom
from friend.models import Friend

class IndexChatView(AsyncLoginRequiredMixin, View):
    http_method_names = ['get']

    async def get(self, request, *args, **kwargs):
        user = request.user

        my_friends_inst = await Friend.objects.filter(user=user).afirst()

        my_friends = await sync_to_async(lambda: my_friends_inst.friends)()

        friends = []

        async for friend in my_friends.aiterator():
            friends.append(friend)
        
        return await sync_to_async(render)(request, 'chat/index.html', {
            'friends': friends
        })




class ChatView(AsyncLoginRequiredMixin, View):
    http_method_names = ['get']

    async def get(self, request, *args, **kwargs):
        to_user = await sync_to_async(UserAccount.objects.get)(username=kwargs['username'])
        from_user = await sync_to_async(UserAccount.objects.get)(username=request.user)

        name = [str(to_user.id), str(from_user.id)]
        name.sort()

        room = await sync_to_async(ChatRoom.objects.get_or_create)(
            room_type=ChatRoom.PERSONAL,
            name=''.join(_ for _ in name)
        )

        return await sync_to_async(render)(request, 'chat/chat.html', {
            'to': to_user,
            'room': room[0].name
        })
