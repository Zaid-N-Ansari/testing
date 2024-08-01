from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FriendRequest, Notification

@receiver(post_save, sender=FriendRequest)
def create_friend_request_notification(sender, instance, created, **kwargs):
	if created:
		Notification.objects.create(
            from_user=instance.from_user,
            to_user=instance.to_user,
            action='sent_friend_request'
        )
		Notification.objects.create(
            from_user=instance.to_user,
            to_user=instance.from_user,
            action='received_friend_request'
        )
