from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст Поста',
            'group': 'Группа',
            'image': 'Изображение'
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относится пост',
            'image': 'Картинка поста'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария'
        }
        help_texts = {
            'text': 'Оставьте ваш комментарий'
        }
