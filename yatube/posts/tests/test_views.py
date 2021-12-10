import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post, User
from ..settings import PAGINATOR_NUM_PAGES

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

SLUG = 'test-slug'
USERNAME = 'MrNobody'
INDEX_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
GROUP_LIST_URL = reverse('posts:group_list', kwargs={'slug': SLUG})
PROFILE_URL = reverse('posts:profile', kwargs={'username': USERNAME})
FOLLOW_URL = reverse('posts:follow_index')
FOLLOWING_URL = reverse(
    'posts:profile_follow',
    kwargs={'username': USERNAME}
)
UNFOLLOWING_URL = reverse(
    'posts:profile_unfollow',
    kwargs={'username': USERNAME}
)
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


class PostViewsTest(TestCase):
    """Тестирование view-функций."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.another = User.objects.create_user(username='Another')
        cls.following = User.objects.create_user(username='Following')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug=SLUG,
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=SimpleUploadedFile(
                name='small.gif',
                content=SMALL_GIF,
                content_type='image/gif'
            )
        )
        cls.EDIT_URL = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.post.pk}
        )
        cls.DETAIL_URL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.pk}
        )
        cls.follow = Follow.objects.create(
            user=cls.another,
            author=cls.user
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.another_client = Client()
        cls.another_client.force_login(cls.another)
        cls.following_client = Client()
        cls.following_client.force_login(cls.following)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()

    def test_page_contains_correct_records(self):
        """Проверка Paginator'a. На первой странице выходит нужное количество
        записей, а на второй странице остальные записи."""
        Post.objects.bulk_create(
            (Post(text='Тестовый текст', author=self.user, group=self.group)
             for _ in range(PAGINATOR_NUM_PAGES + 2))
        )
        reversed_views_name = (
            INDEX_URL,
            GROUP_LIST_URL,
            PROFILE_URL
        )
        additional_pages_records = {
            '': PAGINATOR_NUM_PAGES,
            '?page=2': 3
        }
        for additional_page, num_records in additional_pages_records.items():
            for reversed_view in reversed_views_name:
                with self.subTest(view=reversed_views_name):
                    self.assertEqual(
                        len(self
                            .authorized_client
                            .get(reversed_view + additional_page)
                            .context['page_obj']
                            ),
                        num_records
                    )

    def test_correct_create_new_post(self):
        """Проверка, что пост попал на страницы без искажения данных."""
        urls = (
            INDEX_URL,
            GROUP_LIST_URL,
            PROFILE_URL,
            self.DETAIL_URL,
            FOLLOW_URL,
        )
        for url in urls:
            cache.clear()
            with self.subTest(url=url):
                response = self.another_client.get(url)
                if url != self.DETAIL_URL:
                    self.assertEqual(len(response.context['page_obj']), 1)
                    context = response.context['page_obj'][0]
                else:
                    context = response.context['post']
                self.assertEqual(context.text, self.post.text)
                self.assertEqual(context.group, self.post.group)
                self.assertEqual(context.author, self.post.author)
                self.assertEqual(context.pk, self.post.pk)
                self.assertEqual(context.image, self.post.image)

    def test_post_in_another_group(self):
        """Проверяем что новый пост не попадает на страницу другой группы."""
        another_group = Group.objects.create(
            slug='another_group',
            title='Тестовый заголовок другой группы',
            description='Тестовое описание другой группы'
        )
        ANOTHER_GROUP_URL = reverse(
            'posts:group_list',
            kwargs={'slug': another_group.slug}
        )
        self.assertNotIn(
            self.post,
            self.authorized_client.get(ANOTHER_GROUP_URL).context['page_obj']
        )

    def test_correct_author_in_profile(self):
        """"Проверяем что на странице профиля правильный автор."""
        self.assertEqual(
            self.authorized_client.get(PROFILE_URL).context['author'],
            self.user
        )

    def test_correct_group_in_group_list(self):
        """Проверяем что на странице группы правильная группа."""
        group = self.authorized_client.get(GROUP_LIST_URL).context['group']
        self.assertEqual(group.pk, self.group.pk)
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.description, self.group.description)

    def test_cache_index(self):
        """Тестируем работу кэширования на главной странице."""
        content_before_create = self.authorized_client.get(INDEX_URL).content
        Post.objects.all().delete()
        response_after_create = self.authorized_client.get(INDEX_URL).content
        self.assertEqual(content_before_create, response_after_create)
        cache.clear()
        content_after_clear_cache = self.authorized_client.get(
            INDEX_URL).content
        self.assertNotEqual(content_before_create, content_after_clear_cache)

    def test_following(self):
        """Проверяем, что авторизованный пользователь может подписываться
        на других пользователей и удалять их из подписок."""
        self.following_client.get(FOLLOWING_URL)
        self.assertTrue(
            self.following.follower.filter(user=self.following).exists()
        )

    def test_unfollowing(self):
        """Проверяем, что пользователь отписался от автора."""
        self.another_client.get(UNFOLLOWING_URL)
        self.assertFalse(self.another.follower.filter(
            author=self.user
        ).exists())

    def test_correct_post_in_follow_index(self):
        """Проверяем, что новая запись появляется в ленте тех, кто на него
        подписан и не появляется в ленте тех, кто не подписан."""
        post = Post.objects.create(
            text='Тестовый текст',
            author=self.user
        )
        response_for_unfollower = self.following_client.get(FOLLOW_URL)
        self.assertNotIn(post, response_for_unfollower.context['page_obj'])
