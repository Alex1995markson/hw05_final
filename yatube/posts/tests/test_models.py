from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Post, Group


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(title='R' * 17, slug='Тестовый слаг',
                                         description='Тестовое описание')

        cls.post = Post.objects.create(
            text='R' * 17,
            author=cls.user)

    def test_length_post_text(self):
        """Проверка длины поля post __str__."""
        post = PostModelTest.post
        text = post.__str__()
        self.assertEqual(text, post.text[:15],
                         'Длина вызова __str__ не соотвествует')

    def test_length_group_title(self):
        """Проверка длины поля group __str__."""
        group = PostModelTest.group
        title = group.__str__()
        self.assertEqual(title, group.title[:15],
                         'Длина вызова __str__ не соотвествует')

    def test_verbose_name_post(self):
        """verbose_name в полях Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {'text': 'Текст',
                          'pub_date': 'Дата публикации',
                          'author': 'Автор',
                          'group': 'Группа'
                          }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_verbose_name_group(self):
        """verbose_name в полях Group совпадает с ожидаемым."""
        group = PostModelTest.group
        field_verboses = {'title': 'Заголовок',
                          'slug': 'Ярлык для URL',
                          'description': 'Описание',
                          }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text_post(self):
        """help_text в полях Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_texts = {'text': 'Дайте детальное описание поста',
                       'pub_date': 'Указывается дата публикации',
                       'author': 'Указывается автор поста',
                       'group': 'Указывается принадлежность к группе'
                       }
        for value, expected in field_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_help_text_group(self):
        """help_text в полях Group совпадает с ожидаемым."""
        group = PostModelTest.group
        field_texts = {'title': 'Дайте название группе',
                       'slug': 'Дайте уникальный url',
                       'description': 'Дайте детальное описание группы',
                       }
        for value, expected in field_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)
