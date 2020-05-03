from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Comment

class UserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email')

class UserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('username', 'email')

class CommentCreationForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
