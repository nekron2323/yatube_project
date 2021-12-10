from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

SLUG = 'test-slug'
USERNAME = 'MrNobody'
INDEX_URL = reverse('posts:index')
CREATE_URL = reverse('posts:post_create')
GROUP_LIST_URL = reverse('posts:group_list', kwargs={'slug': SLUG})
PROFILE_URL = reverse('posts:profile', kwargs={'username': USERNAME})
UNEXISTING_PAGE = '/unexisting_page/'
LOGIN_URL = reverse('users:login')
FOLLOW_INDEX_URL = reverse('posts:follow_index')
FOLLOW_URL = reverse('posts:profile_follow', kwargs={'username': USERNAME})
UNFOLLOW_URL = reverse(
    'posts:profile_unfollow',
    kwargs={'username': USERNAME}
)


class PostsURLTest(TestCase):
    """Тестируем, URL-адреса."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.author = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug=SLUG,
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
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
        cls.guest = Client()
        cls.authorized = Client()
        cls.authorized.force_login(cls.user)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def setUp(self):
        cache.clear()

    def test_posts_get_correct_status_code(self):
        """Проверяем, что для пользователей возвращается правильный
        код при GET-запросах."""
        users_urls_names_status_code = [
            [INDEX_URL, self.guest, HTTPStatus.OK],
            [GROUP_LIST_URL, self.guest, HTTPStatus.OK],
            [PROFILE_URL, self.guest, HTTPStatus.OK],
            [self.EDIT_URL, self.guest, HTTPStatus.FOUND],
            [CREATE_URL, self.guest, HTTPStatus.FOUND],
            [UNEXISTING_PAGE, self.guest, HTTPStatus.NOT_FOUND],
            [FOLLOW_INDEX_URL, self.guest, HTTPStatus.FOUND],
            [self.EDIT_URL, self.authorized, HTTPStatus.FOUND],
            [CREATE_URL, self.authorized, HTTPStatus.OK],
            [self.EDIT_URL, self.author_client, HTTPStatus.OK],
            [FOLLOW_INDEX_URL, self.authorized, HTTPStatus.OK],
            [FOLLOW_URL, self.guest, HTTPStatus.FOUND],
            [UNFOLLOW_URL, self.guest, HTTPStatus.FOUND],
        ]
        for url, client, code in users_urls_names_status_code:
            with self.subTest(url=url, client=client):
                self.assertEqual(client.get(url).status_code, code)

    def test_posts_url_correct_templates(self):
        """Проверяем соответствие шаблонов для пользователей."""
        cache.clear()
        urls_users_templates = [
            [INDEX_URL, self.guest, 'posts/index.html'],
            [GROUP_LIST_URL, self.guest, 'posts/group_list.html'],
            [PROFILE_URL, self.guest, 'posts/profile.html'],
            [self.DETAIL_URL, self.guest, 'posts/post_detail.html'],
            [CREATE_URL, self.author_client, 'posts/create_post.html'],
            [self.EDIT_URL, self.author_client, 'posts/create_post.html'],
            [UNEXISTING_PAGE, self.guest, 'core/404.html'],
            [FOLLOW_INDEX_URL, self.authorized, 'posts/follow.html'],
        ]
        for url, client, template in urls_users_templates:
            with self.subTest(url=url, client=client):
                self.assertTemplateUsed(client.get(url), template)

    def test_correct_redirects(self):
        """Проверяем, что для пользователей правильно работает
        перенаправление."""
        initial_users_ending = [
            [self.EDIT_URL, self.guest, self.DETAIL_URL],
            [CREATE_URL, self.guest, LOGIN_URL + '?next=' + CREATE_URL],
            [self.EDIT_URL, self.authorized, self.DETAIL_URL],
            [
                FOLLOW_INDEX_URL,
                self.guest,
                f'{LOGIN_URL}?next={FOLLOW_INDEX_URL}'
            ],
            [FOLLOW_URL, self.guest, f'{LOGIN_URL}?next={FOLLOW_URL}'],
            [UNFOLLOW_URL, self.guest, f'{LOGIN_URL}?next={UNFOLLOW_URL}']
        ]
        for initial_url, client, ending_url in initial_users_ending:
            with self.subTest(url=initial_url, client=client):
                self.assertRedirects(client.get(initial_url), ending_url)
