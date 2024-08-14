from PIL import Image
from os.path import join, exists
from os import mkdir, remove
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic import DetailView
from django.shortcuts import redirect, render
from django.db.models import Q
from django.http import Http404, JsonResponse
from asgiref.sync import sync_to_async
from django.contrib.auth.mixins import LoginRequiredMixin
from base64 import b64decode
from django.core.files import File
from django.contrib.auth.views import (
	LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordChangeView,
    PasswordChangeDoneView
)
from account.models import UserAccount
from friend.models import Friend, FriendRequest
from .forms import (
	LoginForm,
	CustomUserCreationForm,
	CustomPasswordResetForm,
	CustomPasswordResetConfirmForm,
    CustomPasswordChangeForm,
    UserUpdateForm
)


class AsyncLoginRequiredMixin(View):
    async def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account:login')
        return await super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    form_class = LoginForm
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    http_method_names = ['post']
    template_name = "registration/logout.html"


class ProfileView(LoginRequiredMixin, DetailView):
    model = UserAccount
    template_name = 'account/profile.html'

    def get_object(self):
        username = self.kwargs.get('username')
        try:
            return UserAccount.objects.get(username=username)
        except UserAccount.DoesNotExist:
            raise Http404("User does not exist")

    def get_context_data(self, **kwargs):
        user = self.get_object()
        logged_in_user = self.request.user
        context = super().get_context_data(**kwargs)
        friend:Friend = Friend.objects.get_or_create(user=user)[0]
        context['user'] = user
        context['is_friend'] = logged_in_user in friend.friends.all()
        context['fr_from_you'] = FriendRequest.objects.filter(from_user=logged_in_user, to_user=user).exists()
        context['fr_to_you'] = FriendRequest.objects.filter(from_user=user, to_user=logged_in_user).exists()
        context['friends_count'] = friend.friends.count() if logged_in_user == user else ''
        return context


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('password_reset_done')
    template_name = 'registration/password_reset_form.html'


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    success_url = reverse_lazy('password_reset_complete')
    template_name = 'registration/password_reset_confirm.html'


class RegisterView(FormView):
    template_name = 'registration/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('account:login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm


class CustomPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'
    def dispatch(self, request, *args, **kwargs):
        return CustomLogoutView.as_view()(request)


class ProfileEditView(AsyncLoginRequiredMixin, View):
    async def get(self, request, *args, **kwargs):
        form = await sync_to_async(UserUpdateForm)(instance=request.user)
        return await sync_to_async(render)(request, 'account/edit.html', {'form': form})

    async def post(self, request, *args, **kwargs):
        user = request.user
        data = request.POST
        form = await sync_to_async(UserUpdateForm)(data, request.FILES, instance=user)

        if any(data.get(key) for key in ['x', 'y', 's']):
            try:
                await self.handle_image_crop(data, user)
                return redirect(reverse('account:profile', kwargs={'username': user.username}))
            except Exception as e:
                print(f"Image processing error: {e}")

        if form.is_valid():
            await sync_to_async(form.save)()
            return redirect(reverse('account:profile', kwargs={'username': user.username}))

        return await sync_to_async(render)(request, 'account/edit.html', {'form': form})


    async def handle_image_crop(self, data, user):
        x, y, s = (int(float(data[key])) for key in ['x', 'y', 's'])
        img_str = data.get('image')
        temp_url = await self.save_tmp_img(img_str, user)

        await self.process_and_save_image(temp_url, x, y, s, user)

    async def process_and_save_image(self, img_path, x, y, size, user):
        with Image.open(img_path) as img:
            crop_img = img.crop((x, y, x + size, y + size))
            crop_img.save(img_path)

        if user.profile_image.name.split('/')[2] != 'defaultpfi.jpg':
            await sync_to_async(user.profile_image.delete)()

        await sync_to_async(user.profile_image.save)('profile_image.png', File(open(img_path, 'rb')), save=False)

        await user.asave()

        await self.remove_temp_file(img_path)

    async def save_tmp_img(self, img_str, user):
        dir_path = f'temp/{user.pk}'
        if not exists(dir_path):
            mkdir(dir_path)

        url = join(dir_path, f'tmp_{user.pk}_img.png')

        try:
            with open(url, 'wb') as file:
                file.write(b64decode(img_str))
        except Exception as e:
            if str(e) == 'Incorrect padding':
                img_str += '=' * ((4 - len(img_str) % 4) % 4)
                return await self.save_tmp_img(img_str, user)

        return url

    async def remove_temp_file(self, file_path):
        try:
            if exists(file_path):
                remove(file_path)
        except Exception as e:
            print(f"Error removing file {file_path}: {e}")


class SearchView(View):
    http_method_names = ['post']

    async def post(self, request, *args, **kwargs):
        user = request.POST.get('user')
        page_number = int(request.POST.get('page', 1))
        items_per_page = int(request.POST.get('items_per_page', 10))

        try:
            fields = ['username', 'first_name', 'last_name', 'profile_image']

            result = await sync_to_async(
                        lambda: list(
                            UserAccount.objects
                            .filter(
                                Q(username__icontains=user) | 
                                Q(email__icontains=user) | 
                                Q(first_name__icontains=user) | 
                                Q(last_name__icontains=user)
                            )
                            .exclude(username=user)
                            .values_list(*fields)
                        )
                    )()

            paginator = Paginator(result, items_per_page)

            try:
                page_obj = paginator.page(page_number)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)

            result = list(page_obj)
            result = [dict(zip(fields, values)) for values in result]
            result = {'user'+str(cnt): d for cnt, d in enumerate(result)}

            for _, __ in result.items():
                __['profile_image'] = '/media/' + __['profile_image']

            response_data = {
                'result': result if result else None,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                }
            }

            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': str(e)})