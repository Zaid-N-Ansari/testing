from django.contrib import admin
from django.urls import path, include
from app.views import HomeView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
	path('', HomeView.as_view(), name='home'),
	path('account/', include('account.urls', namespace='account')),
	path('friend/', include('friend.urls', namespace='friend'))
]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
