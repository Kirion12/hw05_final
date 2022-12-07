from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Follow, Comment, Group, Post, User

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='UserHasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )

    def setUp(self):
        cache.clear()
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def check_context_contains_page_or_post(self, context, post=False):
        """Проверяем содержимое поста"""
        if post:
            self.assertIn('post', context)
            post = context['post']
        else:
            self.assertIn('page_obj', context)
            post = context['page_obj'][0]
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.image, self.post.image)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': 'test-slug'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
            'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        # Проверяем, что при обращении к name вызывается соотв HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        self.assertEqual(first_post.text, f'{self.post.text}')
        self.assertEqual(first_post.author.username, f'{self.user}')
        self.assertEqual(first_post.group.title, f'{self.group.title}')

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={'slug': 'test-slug'}))
        first_post = response.context['page_obj'][0]
        self.assertEqual(first_post.group.title, f'{self.group.title}')
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        first_post = response.context['page_obj'][0]
        self.assertEqual(first_post.author.username, f'{self.user}')
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        first_post = response.context['post']
        self.assertEqual(first_post.pk, PostsPagesTests.post.pk)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='UserHasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        post_list = []
        for i in range(12):
            post_list.append(Post(
                text=f'Тестовый пост {i}',
                group=self.group,
                author=self.user)
            )
        Post.objects.bulk_create(post_list)

    def test_first_page_contains_ten_records(self):
        """1я страница содержит 10 записей"""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """2я страница содержит 3 записи"""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_group_list_contains_ten_records(self):
        """1я страница группы содержит 10 записей"""
        response = self.client.get(reverse(
            'posts:group_posts', kwargs={'slug': 'test_slug'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_first_page_profile_contains_ten_records(self):
        """1я страница профиля содержит 10 записей"""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'UserHasNoName'}))
        self.assertEqual(len(response.context['page_obj']), 10)


class CommentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='comment')
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.user,
        )
        cls.comment_url = reverse('posts:add_comment', args=['1'])

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_authorized_client_comment(self):
        """Авторизированный пользователь может комментировать"""
        text_comment = 'Kомментарий'
        self.authorized_client.post(self.comment_url,
                                    data={'text': text_comment}
                                    )
        comment = Comment.objects.get(id=self.post.id)
        self.assertEqual(comment.text, text_comment)
        self.assertEqual(Comment.objects.count(), 1)

    def test_guest_client_comment_redirect_login(self):
        """Неавторизированный пользователь не может комментаровать"""
        count_comments = Comment.objects.count()
        self.client.post(CommentTests.comment_url)
        self.assertEqual(count_comments, Comment.objects.count())


class TestCache(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='title',
            slug='slug',
            description='description'
        )
        cls.post = Post.objects.create(
            text='Текст поста',
            group=cls.group,
            author=cls.user,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_cache_index(self):
        """Проверка хранения и очищения кэша для index."""
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(text='Текст поста',
                            author=self.user,)
        response_old = self.authorized_client.get(reverse('posts:index'))
        old_posts = response_old.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        response_new = self.authorized_client.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create(
            username='auth_author',
        )
        cls.user_follow = User.objects.create(
            username='auth_follow',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user_author,
        )

    def setUp(self):
        cache.clear()
        self.author_client = Client()
        self.author_client.force_login(self.user_follow)
        self.follow_client = Client()
        self.follow_client.force_login(self.user_author)

    def test_follow(self):
        """Тест подписки"""
        follow_count = Follow.objects.count()
        response = self.follow_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_follow}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user_follow}
            )
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user_author, author=self.user_follow
            ).exists()
        )

    def test_posts_on_followers(self):
        """Проверка отписки."""
        post = Post.objects.create(
            author=self.user_author,
            text='Тестовый текст'
        )
        Follow.objects.create(
            user=self.user_follow,
            author=self.user_author
        )
        response = self.author_client.get(
            reverse('posts:follow_index')
        )
        post_object = response.context['page_obj']
        self.assertIn(post, post_object)

    def test_posts_on_unfollowers(self):
        """Проверка записей у тех кто не подписан на авторов."""
        post = Post.objects.create(
            author=self.user_author,
            text='Тестовый текст'
        )
        response = self.author_client.get(
            reverse('posts:follow_index')
        )
        post_object = response.context['page_obj']
        self.assertNotIn(post, post_object)
