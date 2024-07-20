from os.path import join, exists
from os import mkdir
from urllib import request
from django.forms import ValidationError
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormView, UpdateView
from django.views.generic import DetailView
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render, get_object_or_404
from django.http import Http404, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import cv2
from django.core.files.storage import FileSystemStorage
from base64 import b64decode
from django.core.files import File
import shutil
from concurrent.futures import ThreadPoolExecutor
from account.models import UserAccount
from friend.models import Friend
from django.contrib.auth.views import (
	LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordChangeView,
    PasswordChangeDoneView,
)
from .forms import (
	LoginForm,
	CustomUserCreationForm,
	CustomPasswordResetForm,
	CustomPasswordResetConfirmForm,
    CustomPasswordChangeForm,
    UserUpdateForm,
)

User = get_user_model()

class CustomLoginView(LoginView):
    form_class = LoginForm
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    http_method_names = ['post']
    template_name = "registration/logout.html"


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'account/profile.html'
    context_object_name = 'user_profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self):
        username = self.kwargs.get('username')
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404("User does not exist")

    def get_context_data(self, **kwargs):
        # context = super().get_context_data(**kwargs)
        # user_profile = self.get_object()
        # friend_instance = get_object_or_404(Friend, user=user_profile)
        # context['friends_count'] = friend_instance.friends.count()
        # return context
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['user'] = user
        return context


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('password_reset_done')
    template_name = 'registration/password_reset_form.html'


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'


class CustomPasswordResetConfirmView( PasswordResetConfirmView):
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


class CustomPasswordChangeView( PasswordChangeView):
    form_class = CustomPasswordChangeForm


class CustomPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'
    def dispatch(self, request, *args, **kwargs):
        return CustomLogoutView.as_view()(request)


class ProfileEditView(LoginRequiredMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        user = request.user
        form = UserUpdateForm(instance=user)
        return render(request, 'account/edit.html', {'form': form})

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.POST
        form = UserUpdateForm(data, request.FILES, instance=user)
        try:
            print(f'valx: {data.get('x')}')
            print(f'valy: {data.get('y')}')
            print(f'valh: {data.get('h')}')
            print(f'valh_type: {type(data.get('h'))}')
            if not(data.get('x') is None or data.get('y') is None or data.get('h') is None):
                x = int(float(str(data.get('x'))))
                y = int(float(str(data.get('y'))))
                h = int(float(str(data.get('h'))))

                print(f'_valx: {x}')
                print(f'_valy: {y}')
                print(f'_valh: {h}')
                imgStr = data.get('image')
                url = self.save_tmp_img(imgStr, user)
                img = cv2.imread(url)

                crop_img = img[y:y+h, x:x+h]
                cv2.imwrite(url, crop_img)

                user.profile_image.delete(save=False)

                user.profile_image.save('profile_image.png', File(open(url, 'rb+')))


                with ThreadPoolExecutor() as executor:
                    executor.submit(self.remove_directory, f'temp/{user.pk}')
        except Exception as e:
            print(e)

        if form.is_valid():
            form.save()
            return redirect(reverse('account:profile', kwargs={'username':user.username}))
        else:
            ValidationError("naahh aah...")
        return render(request, 'account/edit.html', {'form': form})

    def save_tmp_img(self, imgStr, user):
        try:
            if not exists('temp'):
                mkdir('temp')
            if not exists(f'{'temp'}/{user.pk}'):
                mkdir(f'{'temp'}/{user.pk}')
        
            url = join(f'{'temp'}/{user.pk}', f'tmp_{user.pk}_img.png')
            storage = FileSystemStorage(location=url)
            img = b64decode(imgStr)
            with storage.open('', 'wb+') as dest:
                dest.write(img)
                dest.close()
            return url
        except Exception as e:
            if str(e) == 'Incorrect padding':
                imgStr += '=' * ((4 - len(imgStr) % 4) % 4)
                return self.save_tmp_img(imgStr, user)

    def remove_directory(self, path):
        try:
            shutil.rmtree(path)
        except Exception as e:
            print(f"Error removing directory {path}: {e}")
