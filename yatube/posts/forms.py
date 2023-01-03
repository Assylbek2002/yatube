from django.forms import ModelForm
from .models import Post, Comment
from django import forms


class PostForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].empty_label = "Сообщество не выбрано"

    class Meta:
        model = Post
        fields = ("group", "text", "image")


class CommentForm(ModelForm):
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Comment
        fields = ("text", )
