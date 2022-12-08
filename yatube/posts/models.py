from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст Поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата Публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Группа'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор'
    )
    description = models.TextField(
        verbose_name='Описание Группы'
    )

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comment',  # связь пост коммент
        verbose_name='Пост',
        help_text='Комментарий к посту',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comment',  # связь юзер коммент
        verbose_name='Автор',
        help_text='Автор комментария',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария',
    )
    created = models.DateTimeField(
        verbose_name='Создан',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-created', )
        verbose_name_plural = 'Коментарии'
        verbose_name = 'Коментарий'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follows')]

    def __str__(self):
        return f'{self.user} подписался на {self.author}'
