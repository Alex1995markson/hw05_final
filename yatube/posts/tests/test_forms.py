from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.forms import PostForm, CommentForm
from posts.models import Group, Post, Comment

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.title = 'some title for random post'
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(title='text-title1', slug='test-slug',
                                         description='Тестовое описание')
        cls.group_new = Group.objects.create(title='new_title',
                                             slug='new-slug',
                                             description='Описание new')
        cls.group_new_e = Group.objects.create(title='new_title1',
                                               slug='new-slugr',
                                               description='Описание new')
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

        small_gif_edit = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded_edit = SimpleUploadedFile(
            name='small_edit.gif',
            content=small_gif_edit,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text='R' * 17,
            author=cls.user,
            group=cls.group,
            image=uploaded
        )
        cls.form = PostForm()

        cls.comment = Comment.objects.create(post=cls.post,
                                             author=cls.user,
                                             text='some_text')
        cls.form = CommentForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()

        form_data = {
            'text': PostFormTests.post.text,
            'group': PostFormTests.post.group.id,
            'image': PostFormTests.post.image
        }
        response = self.authorized_client.post(
            reverse('main:post_create'),
            data=form_data,
            follow=True
        )
        post_inst = Post.objects.latest('id')
        self.assertRedirects(response,
                             reverse('main:profile', kwargs={'username':
                                     PostFormTests.post.author.username})
                             )

        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post_inst.text, form_data['text'])
        self.assertEqual(post_inst.group.id, form_data['group'])
        self.assertEqual(post_inst.group.id, form_data['group'])
        self.assertTrue(post_inst.image)
        self.assertEqual(response.status_code, 200)

    def test_edit_post(self):
        """Валидная форма изменят запись в Post."""
        posts_count = Post.objects.count()
        post_id = PostFormTests.post.id

        form_data = {
            'text': PostFormTests.title,
            'group': PostFormTests.group_new.id,
            'image': PostFormTests.uploaded_edit
        }
        response = self.authorized_client.post(
            reverse('main:post_edit', kwargs={'post_id':
                    post_id}),
            data=form_data,
            follow=True
        )
        post_inst = Post.objects.get(id=post_id)
        self.assertRedirects(response,
                             reverse('main:post_detail', kwargs={'post_id':
                                     post_id})
                             )
        self.assertEqual(post_inst.text, form_data['text'])
        self.assertEqual(post_inst.group.id, form_data['group'])
        self.assertTrue(form_data['image'])
        self.assertEqual(Post.objects.count(), posts_count)

    def test_create_post_with_unauthorized_user(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'something_test',
            'group': PostFormTests.group_new.id,
            'image': PostFormTests.post.image
        }
        response = self.client.post(
            reverse('main:post_create'),
            data=form_data,
            follow=True
        )
        post_inst = Post.objects.latest('id')
        self.assertRedirects(response,
                             '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertNotEqual(post_inst.text, form_data['text'])
        self.assertNotEqual(post_inst.group.id, form_data['group'])

    def test_edit_post_with_unauthorized_user(self):
        """Валидная форма изменят запись в Post."""
        posts_count = Post.objects.count()

        post_id = PostFormTests.post.id
        form_data = {
            'text': PostFormTests.title,
            'group': PostFormTests.group_new.id,
            'image': PostFormTests.uploaded_edit
        }
        response = self.client.post(
            reverse('main:post_edit', kwargs={'post_id':
                    post_id}),
            data=form_data,
            follow=True
        )
        post_inst = Post.objects.get(id=post_id)
        self.assertRedirects(response,
                             ('/auth/login/?next=/'
                              + f'posts/{post_id}/edit/'))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertNotEqual(post_inst.text, form_data['text'])
        self.assertNotEqual(post_inst.group.id, form_data['group'])

    def test_add_comment_with_authorized_user(self):
        """Валидация добавления комментария в post_detail."""
        comment_count = Comment.objects.count()

        form_data = {
            'text': PostFormTests.comment.text
        }
        response = self.authorized_client.post(
            reverse('main:add_comment', kwargs={'post_id':
                    PostFormTests.post.id}),
            data=form_data,
            follow=True
        )
        comment_inst = Comment.objects.latest('id')
        self.assertRedirects(response,
                             reverse('main:post_detail', kwargs={'post_id':
                                     PostFormTests.post.id})
                             )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertEqual(comment_inst.text, form_data['text'])
        self.assertEqual(response.status_code, 200)

    def test_add_comment_with_unauthorized_user(self):
        """Валидация добавления комментария в post_detail."""
        comment_count = Comment.objects.count()

        form_data = {
            'text': PostFormTests.comment.text
        }
        response = self.client.post(
            reverse('main:add_comment', kwargs={'post_id':
                    PostFormTests.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             ('/auth/login/?next='
                              f'/posts/{PostFormTests.post.id}/comment/'))
        self.assertEqual(Comment.objects.count(), comment_count)

    def test_cache_after_add_post(self):
        """Валидация добавления поста на
           главную страницу с включенным кэшированием"""
        form_data = {
            'text': PostFormTests.title,
            'group': PostFormTests.group_new_e.id,
        }
        self.authorized_client.post(
            reverse('main:post_create'),
            data=form_data,
            follow=True
        )
        response = self.authorized_client.get(reverse('main:index'))
        res = response.content.decode('utf-8')
        self.assertIn(f'<p>{PostFormTests.title}</p>', res)
        created_post = Post.objects.get(text=PostFormTests.title).id
        Post.objects.filter(id=created_post).delete()
        response = self.authorized_client.get(reverse('main:index'))
        self.assertIn(f'<p>{PostFormTests.title}</p>',
                      response.content.decode('utf-8'))
        cache.clear()
        response = self.authorized_client.get(reverse('main:index'))
        self.assertNotIn(f'<p>{PostFormTests.title}</p>',
                         response.content.decode('utf-8'))
