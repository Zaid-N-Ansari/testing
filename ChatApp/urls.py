from django.contrib import admin
from django.urls import path, include
from app.views import HomeView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
	path('', HomeView.as_view(), name='home'),
	path('account/', include('account.urls', namespace='account')),
	path('friend/', include('friend.urls', namespace='friend')),
	path('chat/', include('chat.urls', namespace='chat')),
	path('group/', include('chat.urls', namespace='group')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
