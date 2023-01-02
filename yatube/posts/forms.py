from django.forms import ModelForm
from .models import Post


class PostForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].empty_label = "Сообщество не выбрано"

    class Meta:
        model = Post
        fields = ("group", "text", )
