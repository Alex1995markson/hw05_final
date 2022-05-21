from django import forms
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.models import Follow, Group, Post, Comment

User = get_user_model()


def create_dict_context(res_cont, post_obj):
    dict_context = {}
    for t in res_cont['page_obj']:
        dict_context[t.pk] = post_obj.id
        dict_context[t.group.title] = post_obj.group.title
        dict_context[t.author] = post_obj.author
        dict_context[t.group.slug] = post_obj.group.slug
        dict_context[t.group.description] = (post_obj.group.description)
        dict_context[t.image] = post_obj.image
    return dict_context


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_not_athor = User.objects.create_user(
            username='auth_not_author')
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(title='text-title1', slug='test-slug',
                                         description='Тестовое описание')

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
            text='R' * 17,
            author=cls.user,
            group=cls.group,
            image=uploaded
        )

        cls.comment = Comment.objects.create(post=cls.post, author=cls.user,
                                             text='some_text')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('main:index'): 'posts/index.html',
            reverse('main:profile', kwargs={'username':
                    PostPagesTests.post.author}):
                        'posts/profile.html',
            reverse('main:group', kwargs={'slug':
                    PostPagesTests.post.group.slug}):
                        'posts/group_list.html',
            reverse('main:post_detail', kwargs={'post_id':
                    PostPagesTests.post.id}):
                        'posts/post_detail.html',
            reverse('main:post_create'): 'posts/post_create.html',
            reverse('main:post_edit', kwargs={'post_id':
                    PostPagesTests.post.id}):
                        'posts/post_create.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('main:index'))
        d_context = create_dict_context(response.context,
                                        PostPagesTests.post)

        for key, value in d_context.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)

    def test_post_detail_page_show_correct_content(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('main:post_detail',
                    kwargs={'post_id': PostPagesTests.post.id}))
        post_ex = response.context['post'].text
        post_author = response.context['user'].username
        post_img = response.context['post'].image
        self.assertEqual(post_ex, PostPagesTests.post.text)
        self.assertEqual(post_author, PostPagesTests.post.author.username)
        self.assertEqual(post_img, PostPagesTests.post.image)

    def test_profile_page_show_correct_content(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('main:group', kwargs={'slug':
                    PostPagesTests.post.group.slug}))
        d_context = create_dict_context(response.context, PostPagesTests.post)
        for key, value in d_context.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)

    def test_group_posts_page_show_correct_content(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('main:profile', kwargs={'username':
                    PostPagesTests.post.author}))

        d_context = create_dict_context(response.context,
                                        PostPagesTests.post)

        for key, value in d_context.items():
            with self.subTest(key=key):
                self.assertEqual(key, value)

    def test_edit_page_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('main:post_edit', kwargs={'post_id':
                    PostPagesTests.post.id}))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)

                self.assertIsInstance(form_field, expected)

    def test_create_page_show_correct_context(self):
        """Шаблон edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('main:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)

                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.page_item_count = 10
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(title='text-title1', slug='test-slug',
                                         description='Тестовое описание')
        for number in range(13):
            Post.objects.create(
                text='R' * 17,
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        cache.clear()

    def test_index_page_contains_ten_records(self):
        response = self.client.get(reverse('main:index'))
        self.assertEqual(len(response.context['page_obj']),
                         PaginatorViewsTest.page_item_count)

    def test_profile_page_contains_three_records(self):
        response = self.client.get(
            reverse('main:profile', kwargs={'username':
                    PaginatorViewsTest.user}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_posts_page_contains_ten_records(self):
        response = self.client.get(
            reverse('main:group', kwargs={'slug':
                    PaginatorViewsTest.group.slug}))
        self.assertEqual(len(response.context['page_obj']),
                         PaginatorViewsTest.page_item_count)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(title='text-title1', slug='test-slug',
                                         description='Тестовое описание')
        cls.author = User.objects.create_user(username='leo')
        cls.author_new = User.objects.create_user(username='alexz')

        for number in range(13):
            Post.objects.create(
                text='R' * 17,
                author=cls.author_new,
                group=cls.group
            )

        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_follow_for_new_author(self):
        self.authorized_client.get(
            reverse(
                'main:profile_follow',
                kwargs={'username': FollowViewsTest.author_new.username}
            )
        )
        self.assertTrue(
            Follow.objects.filter(user=self.user,
                                  author=self.author_new).exists(),
            'Подписка не добавлена!'
        )

    def test_unfollow_for_current_author(self):
        self.authorized_client.get(
            reverse(
                'main:profile_unfollow',
                kwargs={'username': FollowViewsTest.author_new.username}
            )
        )
        self.assertFalse(
            Follow.objects.filter(user=self.user,
                                  author=self.author_new).exists(),
            'Подписка не удалена!'
        )
