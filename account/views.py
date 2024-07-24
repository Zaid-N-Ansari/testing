from os.path import join, exists
from os import mkdir
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.views.generic import DetailView
from django.shortcuts import redirect, render
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import cv2
from django.core.files.storage import FileSystemStorage
from base64 import b64decode
from django.core.files import File
import shutil
from concurrent.futures import ThreadPoolExecutor
from django.contrib.auth.views import (
	LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordChangeView,
    PasswordChangeDoneView,
)
from account.models import UserAccount
from friend.models import Friend
from .forms import (
	LoginForm,
	CustomUserCreationForm,
	CustomPasswordResetForm,
	CustomPasswordResetConfirmForm,
    CustomPasswordChangeForm,
    UserUpdateForm,
)

class CustomLoginView(LoginView):
    form_class = LoginForm
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    http_method_names = ['post']
    template_name = "registration/logout.html"


class ProfileView(LoginRequiredMixin, DetailView):
    model = UserAccount
    template_name = 'account/profile.html'
    context_object_name = 'user_profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self):
        username = self.kwargs.get('username')
        try:
            return UserAccount.objects.get(username=username)
        except UserAccount.DoesNotExist:
            raise Http404("User does not exist")

    def get_context_data(self, **kwargs):
        user = self.get_object()
        context = super().get_context_data(**kwargs)
        user_acc = Friend.objects.get_or_create(user=user)
        context['friends_count'] = user_acc[0].friends.count()
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
        form = UserUpdateForm(instance=request.user)
        return render(request, 'account/edit.html', {'form': form})

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.POST
        form = UserUpdateForm(data, request.FILES, instance=user)
        try:
            if data.get('x') or data.get('y') or data.get('s'):
                x = int(float(data.get('x')))
                y = int(float(data.get('y')))
                s = int(float(data.get('s')))

                imgStr = data.get('image')

                url = self.save_tmp_img(imgStr, user)

                img = cv2.imread(url)

                crop_img = img[y:y+s, x:x+s]

                cv2.imwrite(url, crop_img)

                user.profile_image.delete()

                user.profile_image.save('profile_image.png', File(open(url, 'rb')))

                user.save()

                with ThreadPoolExecutor() as executor:
                    executor.submit(self.remove_directory, f'temp/{user.pk}')
                return redirect(reverse('account:profile', kwargs={'username': user.username}))
        except Exception as e:
            print(e)

        if form.is_valid():
            form.save()
            return redirect(reverse('account:profile', kwargs={'username': user.username}))
        return render(request, 'account/edit.html', {'form': form})

    def save_tmp_img(self, imgStr, user):
        try:
            if not exists('temp'):
                mkdir('temp')
            if not exists(f'temp/{user.pk}'):
                mkdir(f'temp/{user.pk}')
        
            url = join(f'temp/{user.pk}', f'tmp_{user.pk}_img.png')
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


class SearchView(View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        user = request.POST.get('user')
        page_number = request.POST.get('page', 1)  # Get the requested page number, default to 1
        items_per_page = request.POST.get('items_per_page', 10)  # Number of items per page

        try:
            # Fields to return
            fields = ['username', 'first_name', 'last_name', 'profile_image']

            # Query the database
            result = UserAccount.objects.filter(
                Q(username__icontains=user) |
                Q(email__icontains=user) |
                Q(first_name__icontains=user) |
                Q(last_name__icontains=user)
            ).order_by('last_name').values_list('username', 'first_name', 'last_name', 'profile_image')

            # Create a Paginator object
            paginator = Paginator(result, items_per_page)

            try:
                # Get the requested page
                page_obj = paginator.page(page_number)
            except PageNotAnInteger:
                # If page is not an integer, deliver the first page
                page_obj = paginator.page(1)
            except EmptyPage:
                # If page is out of range, deliver the last page of results
                page_obj = paginator.page(paginator.num_pages)

            # Prepare the paginated results
            result = list(page_obj)
            result = [dict(zip(fields, values)) for values in result]
            result = {'user'+str(cnt): d for cnt, d in enumerate(result)}

            # Update the profile_image paths
            for key, value in result.items():
                if 'profile_image' in value:
                    value['profile_image'] = '/media/' + value['profile_image']

            # Include pagination metadata
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
