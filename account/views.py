import json
from os.path import join
from django.urls import reverse_lazy
from django.views.generic.edit import FormView, UpdateView
from django.views.generic import DetailView
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
	LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordChangeView,
    PasswordChangeDoneView,
)
from PIL import Image
import base64
from io import BytesIO
import cv2

from ChatApp.settings import BASE_DIR
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
        instance = form.save(commit=False)

        cropped_image_data = self.request.POST.get('cropped_image') | None
        if cropped_image_data:
            cropped_image_data = cropped_image_data.split(',')[1]
            cropped_image_data = base64.b64decode(cropped_image_data)
            cropped_image = Image.open(BytesIO(cropped_image_data))
            cropped_image_io = BytesIO()
            cropped_image.save(cropped_image_io, format='JPEG')
            instance.profile_image.save(f'{instance.pk}_profile.jpg', cropped_image_io, save=False)

        instance.save()
        return redirect(self.success_url)

from django.core.files.storage import FileSystemStorage
from base64 import b64decode
from django.core.files import File
@login_required
def edit_done(request, *args, **kwargs):
    dic = {}
    if request.method == 'POST':
        data = request.POST
        user = request.user
        keys = ['x','y','w','h', 'image']
        if any(data.get(key) is not None for key in keys):
            [cropX,cropY,cropW,cropH,imgStr] = [data.get(key) for key in keys]


            try:
                url = join(f'{BASE_DIR}/temp/{user.pk}', f'{user.pk}_tmp_img.png')

                storage = FileSystemStorage(location=url)

                img = b64decode(imgStr)

                with storage.open('', 'wb+') as dest:
                    dest.write(img)
                    dest.close()
            except Exception as e:
                if str(e) == 'Incorrect padding':
                    imgStr += '=' * ((4 - len(imgStr) % 4) % 4)
                url = join(f'{BASE_DIR}/temp/{user.pk}', f'{user.pk}_tmp_img.png')

                storage = FileSystemStorage(location=url)

                img = b64decode(imgStr)

                with storage.open('', 'wb+') as dest:
                    dest.write(img)
                    dest.close()

            crop_img = img[cropY:cropY+cropH, cropX:cropX+cropW]

            cv2.imwrite(url, crop_img)

            user.profile_image.delete()

            user.profile_image.save('profile_image.png', File(open(url, 'rb')))

            user.save()

            dic['result'] = 'success'
        
        dic['result'] = 'Points Not Defined'

        return JsonResponse(dic)
