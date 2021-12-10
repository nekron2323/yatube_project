import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
USERNAME = 'MrNobody'
POST_CREATE_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', kwargs={'username': USERNAME})
LOGIN_URL = reverse('users:login')
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


class PostFormsTest(TestCase):
    """Тестируем формы."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.another_user = User.objects.create_user(
            username='AnotherMrNobody'
        )
        cls.form = PostForm()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.another_group = Group.objects.create(
            title='Другой тестовый заголовок',
            slug='another_test_slug',
            description='Другое тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )
        cls.EDIT_URL = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.post.pk}
        )
        cls.DETAIL_URL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.pk}
        )
        cls.authorized_user = Client()
        cls.another_client = Client()
        cls.guest = Client()
        cls.authorized_user.force_login(cls.user)
        cls.another_client.force_login(cls.another_user)
        cls.ADD_COMMENT_URL = reverse(
            'posts:add_comment',
            kwargs={'post_id': cls.post.pk}
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        super().setUp()

    def test_post_create(self):
        """Проверяем, что создается новый пост и после создания переходит
        на страницу профиля автора."""
        posts = set(Post.objects.all())
        form_data = {
            'text': 'Новый тестовый текст',
            'group': self.group.pk,
            'image': SimpleUploadedFile(
                name='small.gif',
                content=SMALL_GIF,
                content_type='image/gif'
            )
        }
        response = self.authorized_user.post(
            POST_CREATE_URL,
            form_data,
            follow=True
        )
        posts = set(response.context['page_obj']) - posts
        self.assertEqual(len(posts), 1)
        post = posts.pop()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])
        self.assertTrue(post.image)
        self.assertEqual(post.author, self.user)
        self.assertRedirects(
            response,
            PROFILE_URL
        )

    def test_post_edit(self):
        """Проверяем что изменяется пост и не создается новый. После создания
        перенаправляет на страницу этого поста."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный тестовый текст',
            'group': self.another_group.pk,
            'image': SimpleUploadedFile(
                name='small.gif',
                content=SMALL_GIF,
                content_type='image/gif'
            )
        }
        response = self.authorized_user.post(
            self.EDIT_URL,
            data=form_data,
            follow=True
        )
        post = response.context['post']
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.pk, form_data['group'])
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.pk, self.post.pk)
        self.assertTrue(post.image)
        self.assertRedirects(response, self.DETAIL_URL)

    def test_post_context_correct_form(self):
        """Проверяем, что шаблоны создания и редактирования постов
        сформированы с правильным контекстом."""
        view_names = (
            POST_CREATE_URL,
            self.EDIT_URL
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        for url in view_names:
            context = self.authorized_user.get(url).context
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_comment_guest_create(self):
        """Проверяем, что гость не может создать комментарий."""
        comments = Comment.objects.all()
        comments_count = comments.count()
        form_data = {
            'text': 'Тестовый текст комментария',
        }
        self.guest.post(
            self.ADD_COMMENT_URL,
            form_data,
            follow=True
        )
        self.assertEqual(comments_count, Comment.objects.count())
        self.assertQuerysetEqual(comments, Comment.objects.all())

    def test_post_cant_be_edited_by_guest(self):
        """Проверяем, что гость не может отредактировать пост."""
        form_data = {
            'text': 'Текст поста',
            'group': self.group.pk,
            'image': SimpleUploadedFile(
                name='small.gif',
                content=SMALL_GIF,
                content_type='image/gif'
            )
        }
        clients = (
            self.guest,
            self.another_client
        )
        for client in clients:
            with self.subTest(client=client):
                response = self.client.post(
                    self.EDIT_URL,
                    form_data,
                    follow=True
                )
                post = response.context['post']
                self.assertEqual(self.post.text, post.text)
                self.assertEqual(self.group, post.group)
                self.assertEqual(self.post.author, post.author)
                self.assertEqual(self.post.image, post.image)
                self.assertEqual(self.post.pk, post.pk)
                self.assertRedirects(response, self.DETAIL_URL)

    def test_add_new_comment(self):
        """Проверяем, что после успешной отправки комментарий появляется на
        странице поста."""
        comments = set(Comment.objects.all())
        form_data = {
            'text': 'Тестовый текст комментария',
        }
        response = self.authorized_user.post(
            self.ADD_COMMENT_URL,
            form_data,
            follow=True
        )
        comments_count = response.context['post'].comments.count()
        self.assertEqual(comments_count, 1)
        comment = (
            set(response.context['post'].comments.all()) - comments
        ).pop()
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.text, form_data['text'])
