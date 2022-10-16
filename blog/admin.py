from django.contrib import admin
from blog.models import Post, Tag, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'published_at',
    )
    raw_id_fields = (
        'author',
        'likes',
        'tags',
    )


class PostsInstanceInline(admin.TabularInline):
    model = Post.tags.through
    raw_id_fields = ('post',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    inlines = [PostsInstanceInline]
    list_display = (
        'title',
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'published_at',
    )
    raw_id_fields = (
        'post',
        'author',
    )
