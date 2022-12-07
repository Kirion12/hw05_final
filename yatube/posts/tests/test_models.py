from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

        def test_model_post_have_correct_object_name(self):
            """У модели Post корректно работает __str__."""
            post = PostModelTest.post
            expected_object_name = post.text
            self.assertEqual(expected_object_name, str(post))

        def test_model_post_have_correct_object_name(self):
            """У модели Post корректно работает __str__."""
            post = PostModelTest.post
            expected_object_name = post.text
            self.assertEqual(expected_object_name, str(post))

        def test_post_have_correct_verbose_name(self):
            """У модели Post поля verbose_name совпадают с ожидаемыми"""
            post = PostModelTest.post
            field_verbose_name = {
                'text': 'Тестовый пост',
                'group': 'Тестовая группа',
                'pub_date': 'Дата публикации',
                'author': 'Автор',
            }
            for field, expected in field_verbose_name.items():
                with self.subTest(field=field):
                    self.assertEqual(
                        post._meta.get_field(field).verbose_name, expected)
