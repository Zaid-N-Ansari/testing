from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from account.models import UserAccount
from account.views import AsyncLoginRequiredMixin
from asgiref.sync import sync_to_async
from django.utils.crypto import get_random_string
from chat.models import ChatRoom, Group
from friend.models import Friend
from .forms import GroupCreationForm


class IndexChatView(AsyncLoginRequiredMixin, View):
    http_method_names = ['get', 'post']

    async def get(self, request, *args, **kwargs):
        form = GroupCreationForm(user=request.user)

        my_friends_inst = await sync_to_async(lambda: Friend.objects.filter(user=request.user).first())()
        if my_friends_inst:
            my_friends_ids = await sync_to_async(lambda: list(my_friends_inst.friends.values_list('id', flat=True)))()
        else:
            my_friends_ids = []

        friends = await sync_to_async(lambda: UserAccount.objects.filter(id__in=my_friends_ids))()
        groups = await sync_to_async(lambda: Group.objects.filter(participant=request.user))()

        return await sync_to_async(render)(request, 'chat/chat.html', {
            'friends': friends,
            'groups': groups,
            'form': form
        })
    
    async def post(self, request, *args, **kwargs):
        form = GroupCreationForm(request.POST, request.FILES, user=request.user)
        if await sync_to_async(form.is_valid)():
            group:Group = await sync_to_async(form.save)(commit=False)
            group.admin = request.user
            chatroom_name = get_random_string(16)
            chatroom, _ = await sync_to_async(ChatRoom.objects.get_or_create)(name=chatroom_name, room_type=ChatRoom.GROUP)
            group.chatroom = chatroom
            await sync_to_async(group.save)()
            await sync_to_async(group.participant.set)(form.cleaned_data['participant'])
            await group.participant.aadd(request.user)

        my_friends = await sync_to_async(lambda: list(Friend.objects.filter(user=request.user).values_list('friends', flat=True)))()
        friends = await sync_to_async(lambda: UserAccount.objects.filter(id__in=my_friends))()

        groups = await sync_to_async(lambda: Group.objects.filter(participant=request.user))()

        return await sync_to_async(redirect)('chat:index',permanent=True)





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

