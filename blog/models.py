from django.db import models
from django.db.models import Count, Prefetch
from django.urls import reverse
from django.contrib.auth.models import User


class PostQuerySet(models.QuerySet):
    def fetch_with_comments_count(self):
        posts_ids = [post.id for post in self]
        posts_with_comments = Post.objects.filter(id__in=posts_ids).annotate(comments_count=Count('comments'))
        ids_and_comments = posts_with_comments.values_list('id', 'comments_count')
        count_for_id = dict(ids_and_comments)
        for post in self:
            post.comments_count = count_for_id[post.id]
        return self

    def fresh(self):
        return self.order_by(
            '-published_at',
        )

    def popular(self):
        return self.annotate(
            likes_count=Count('likes'),
        ).order_by(
            '-likes_count',
        )

    def prefetch_authors(self):
        return self.prefetch_related(
            'author',
        )

    def prefetch_tags_and_count_posts(self):
        tags_prefetch = Prefetch(
            'tags',
            queryset=Tag.objects.annotate(posts_count=Count('posts')),
            to_attr='tags_posts')

        return self.prefetch_related(
            tags_prefetch,
        )


class TagQuerySet(models.QuerySet):
    def fetch_with_posts_count(self):
        tags_ids = [tag.id for tag in self]
        tags_with_posts = Tag.objects.filter(id__in=tags_ids).annotate(posts_count=Count('posts'))
        ids_and_posts = tags_with_posts.values_list('id', 'posts_count')
        count_for_id = dict(ids_and_posts)
        for tag in self:
            tag.posts_count = count_for_id[tag.id]
        return self

    def popular(self):
        return self.annotate(posts_count=Count('posts')).order_by('-posts_count')


class Post(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка')
    published_at = models.DateTimeField('Дата и время публикации')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True},
    )
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True,
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги',
    )

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})


class Tag(models.Model):
    title = models.CharField(
        'Тег',
        max_length=20,
        unique=True,
    )

    objects = TagQuerySet.as_manager()

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Пост, к которому написан',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации')

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'
