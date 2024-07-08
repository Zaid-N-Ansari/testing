from django.urls import path
from .views import (
	RegisterView,
	ProfileView,
	CustomLoginView,
	CustomLogoutView,
	CustomPasswordResetView,
	CustomPasswordResetConfirmView,
)
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetCompleteView

urlpatterns = [
	path('login/', CustomLoginView.as_view(), name='login'),

	path('logout/', CustomLogoutView.as_view(), name='logout'),

	path('register/', RegisterView.as_view(), name='register'),

	path('profile/<str:username>/', ProfileView.as_view(), name='profile'),

    # path(
    #     "password_change/", views.PasswordChangeView.as_view(), name="password_change"
    # ),

    # path(
    #     "password_change/done/",
    #     views.PasswordChangeDoneView.as_view(),
    #     name="password_change_done",
    # ),

    path("password-reset/",
		CustomPasswordResetView.as_view(),
		name="password_reset"
	),

    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),

    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    )
]
