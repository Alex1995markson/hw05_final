from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок',
                             help_text='Дайте название группе')
    slug = models.SlugField(unique=True, verbose_name='Ярлык для URL',
                            help_text='Дайте уникальный url')
    description = models.TextField(verbose_name='Описание',
                                   help_text='Дайте детальное описание группы')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title[:15]


class Post(models.Model):
    text = models.TextField(verbose_name='Текст',
                            help_text='Дайте детальное описание поста')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации',
                                    help_text='Указывается дата публикации',
                                    db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор', related_name="posts",
                               help_text='Указывается автор поста')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              blank=True, null=True, related_name="posts",
                              verbose_name='Группа',
                              help_text='Указывается принадлежность к группе')
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Добавить картинки к посту'
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             verbose_name='Пост', related_name="comments",
                             help_text='Указывается поста к комментрию')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор комментария',
                               related_name="comments",
                               help_text='Указывается автор комментария')
    text = models.TextField(verbose_name='Комментарий',
                            help_text='Дайте комментарий')
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата публикации',
                                   help_text='Указывается дата публикации')

    class Meta:
        ordering = ['-created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Последователь',
                             help_text='Указывается автор комментария')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='За кем следят',
                               help_text='Указывается автор комментария')
    created = models.DateTimeField(auto_now_add=True)
