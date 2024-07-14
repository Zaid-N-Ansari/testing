from os.path import join, exists
from django.urls import reverse_lazy
from django.views.generic.edit import FormView, UpdateView
from django.views.generic import DetailView
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import cv2
from json import dumps
from django.core.files.storage import FileSystemStorage
from base64 import b64decode
from django.core.files import File
from os import mkdir
import shutil
from concurrent.futures import ThreadPoolExecutor
from django.views import View
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

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404("User does not exist")


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
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class CustomPasswordChangeView( PasswordChangeView):
    form_class = CustomPasswordChangeForm


class CustomPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    def dispatch(self, request, *args, **kwargs):
        return CustomLogoutView.as_view()(request)


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'account/edit.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        return redirect(self.success_url)


class ProfileImageView(LoginRequiredMixin, View):
    def save_tmp_profile_img(self, imgStr, user):
        try:
            if not exists('temp'):
                mkdir('temp')
            if not exists(f'temp/{user.pk}'):
                mkdir(f'temp/{user.pk}')
                
            url = join(f'temp/{user.pk}', f'{user.pk}_profile_img.png')
            storage = FileSystemStorage(location=url)
            img = b64decode(imgStr)
            with storage.open('', 'wb+') as dest:
                dest.write(img)
                dest.close()
            
            return url
        except Exception as e:
            if str(e) == 'Incorrect padding':
                imgStr += '=' * ((4 - len(imgStr) % 4) % 4)
                return self.save_tmp_profile_img(imgStr, user)

    def remove_directory(self, path):
        try:
            shutil.rmtree(path)
        except Exception as e:
            print(f"Error removing directory {path}: {e}")
            
    def get(self, request, *args, **kwargs):
        print(f'\n\n{request.POST.get('first_name')}\n\n{args}\n\n{kwargs}\n\n{request}')
        payload = {
            'result': request.method,
            'firstname': kwargs
		}
        return HttpResponse(dumps(payload), content_type='application/json')

    def post(self, request, *args, **kwargs):
        payload = {}
        user = request.user
        try:
            imgStr = request.POST.get('image')
            url = self.save_tmp_profile_img(imgStr, user)
            img = cv2.imread(url)
            cropX = int(float(str(request.POST.get('x'))))
            cropY = int(float(str(request.POST.get('y'))))
            cropW = int(float(str(request.POST.get('w'))))
            cropH = int(float(str(request.POST.get('h'))))

            if cropX < 0:
                cropX = 0
            if cropY < 0:
                cropY = 0

            crop_img = img[cropY:cropY+cropH, cropX:cropX+cropW]

            cv2.imwrite(url, crop_img)

            user.profile_image.delete()

            user.profile_image.save('profile_image.png', File(open(url, 'rb')))

            user.save()

            payload['result'] = 'success'
			
            with ThreadPoolExecutor() as executor:
                executor.submit(self.remove_directory, f'temp/{user.pk}')

        except Exception as e:
            print(e)

		
        return HttpResponse(dumps(payload), content_type='application/json')
