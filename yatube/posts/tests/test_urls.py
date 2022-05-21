from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from django.core.cache import cache


from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_not_athor = User.objects.create_user(
            username='auth_not_author')
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(title='R' * 17, slug='test-slug',
                                         description='Тестовое описание')

        cls.post = Post.objects.create(
            text='R' * 17,
            author=cls.user)

    def setUp(self):
        self.user = User.objects.get(username='auth')

        self.user_not_athor = User.objects.get(username='auth_not_author')
        self.authorized_client_not_author = Client()
        (self.authorized_client_not_author.
            force_login(self.user_not_athor))

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template_with_authrized_user_author(self):
        """URL-адрес использует соответствующий шаблон для пользователя,
           который аворизован и является автором поста
        """
        cache.clear()
        templates_url_names = {
            '/': 'posts/index.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            '/create/': 'posts/post_create.html',
            f'/posts/{self.post.id}/edit/': 'posts/post_create.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_with_authrized_user(self):
        """URL-адрес использует соответствующий шаблон, для
           авторизированого пользователя не автора поста"""
        cache.clear()
        templates_url_names = {
            '/': 'posts/index.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            '/create/': 'posts/post_create.html',
            f'/posts/{self.post.id}/edit/': 'posts/post_create.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_with_user(self):
        """URL-адрес использует соответствующий шаблон для
            обычного пользователя"""
        cache.clear()
        templates_url_names = {
            '/': 'posts/index.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            '/auth/login/?next=/create/': 'users/login.html',
            f'/auth/login/?next=/posts/{self.user.username}/edit/':
                'users/login.html'

        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page_returns_404(self):
        """Несуществующая страница вернёт ошибку 404."""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        response = self.authorized_client_not_author.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
