from django import forms
from account.models import UserAccount

from friend.models import Friend
from.models import Group

class GroupCreationForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'group_image', 'participant', 'desc']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(GroupCreationForm, self).__init__(*args, **kwargs)
        if self.user:
            friends_ids = Friend.objects.filter(user=self.user).values_list('friends', flat=True)
            self.fields['participant'].queryset = UserAccount.objects.filter(id__in=friends_ids)
