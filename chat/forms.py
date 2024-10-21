from django import forms
from django.contrib.auth.models import User
from .models import GroupChat

class MultipleUsersField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.first_name} {obj.last_name}'


class SingleUserField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.first_name} {obj.last_name}'


class GroupChatForm(forms.ModelForm):
    class Meta:
        model = GroupChat
        fields = ['name', 'participants', 'group_image']

    name = forms.CharField(max_length=50)
    participants = MultipleUsersField(queryset=None)
    group_image = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        self.logged_user = kwargs.pop('logged_user')
        super().__init__(*args, **kwargs)
        self.fields['participants'].queryset = User.objects.filter(
            profile__in=self.logged_user.profile.friends.all())

    def clean_participants(self):
        participants = self.cleaned_data['participants']
        friends = self.logged_user.profile.friends.all()
        is_subset = not participants.exclude(pk__in=friends).exists()
        if not is_subset:
            raise forms.ValidationError('You can only add friends to the group chat')
        else:
            return participants


