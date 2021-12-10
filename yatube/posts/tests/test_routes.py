
from django.test import TestCase
from django.urls.base import reverse

USERNAME = 'MrNobody'
POST_ID = 1
SLUG = 'test_slug'


class PostRoutesTest(TestCase):
    """Проверяем маршруты."""

    def test_correct_routes(self):
        urls_routes_names_kwargs = [
            ['/', 'index', {}],
            ['/create/', 'post_create', {}],
            [f'/group/{SLUG}/', 'group_list', {'slug': SLUG}],
            [f'/profile/{USERNAME}/', 'profile', {'username': USERNAME}],
            [f'/posts/{POST_ID}/', 'post_detail', {'post_id': POST_ID}],
            [f'/posts/{POST_ID}/edit/', 'post_edit', {'post_id': POST_ID}],
            ['/follow/', 'follow_index', {}],
            [
                f'/profile/{USERNAME}/follow/',
                'profile_follow',
                {'username': USERNAME}
            ],
            [
                f'/profile/{USERNAME}/unfollow/',
                'profile_unfollow',
                {'username': USERNAME}
            ],
            [
                f'/posts/{POST_ID}/comment/',
                'add_comment',
                {'post_id': POST_ID}
            ],
        ]
        for url, route, kwargs in urls_routes_names_kwargs:
            with self.subTest(url=url):
                self.assertEqual(url, reverse(
                    f'posts:{route}',
                    kwargs=kwargs)
                )
