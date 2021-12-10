from django.test import TestCase

from ..models import Group, Post, User


class PostModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='MrNobody')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Т' * 100,
            author=cls.user
        )

    def test_models_have_correct_object_name(self):
        """Проверяем, что у моделей Post, Group приложения posts корректно
        работает метод __str__."""
        models_str = {
            self.post: self.post.text[:15],
            self.group: self.group.title
        }
        for value, expected in models_str.items():
            with self.subTest(value=value):
                self.assertEqual(str(value), expected)

    def test_model_posts_fields_have_correct_verboses_name(self):
        """Проверяем, что у модели Post корректные verbose_name у полей."""
        field_verbose_name = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for value, expected in field_verbose_name.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Post._meta.get_field(value).verbose_name,
                    expected
                )

    def test_model_posts_fields_have_correct_help_text(self):
        """Проверяем, что поля text, group модели Post имеют корректный
        текст справки."""
        fields_help_text = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        for value, expected in fields_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Post._meta.get_field(value).help_text,
                    expected
                )
