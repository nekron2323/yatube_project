from http import HTTPStatus

from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        super().setUp()
        self.guest_client = Client()

    def test_about_author(self):
        """Проверяет доступ к странице "Об авторе"."""
        self.assertEqual(
            self.guest_client.get('/about/author/').status_code,
            HTTPStatus.OK
        )

    def test_about_tech(self):
        """Проверяет доступ к странице "Технологии"."""
        self.assertEqual(
            self.guest_client.get('/about/tech/').status_code,
            HTTPStatus.OK
        )
