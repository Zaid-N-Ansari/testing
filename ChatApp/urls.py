from django.contrib import admin
from django.urls import path, include
from app.views import home_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
	path('', home_view, name='home'),
	path('account/', include('account.urls', namespace='account')),
	# path('friend/', include('friend.urls'))
]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
