from django.shortcuts import render

from blog.models import Post, Tag


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags_posts],
        'first_tag_title': post.tags_posts[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def index(request):
    most_popular_posts = Post.objects.popular()[:5].\
        prefetch_authors().\
        prefetch_tags_and_count_posts().\
        fetch_with_comments_count()
    most_fresh_posts = Post.objects.fresh()[:5].\
        prefetch_authors().\
        prefetch_tags_and_count_posts().\
        fetch_with_comments_count()
    most_popular_tags = Tag.objects.popular()[:5].fetch_with_posts_count()

    context = {
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }

    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = Post.objects.get(slug=slug)
    comments = post.comments.select_related('author')
    most_popular_posts = Post.objects.popular()[:5].\
        prefetch_authors().\
        prefetch_tags_and_count_posts().\
        fetch_with_comments_count()
    most_popular_tags = Tag.objects.popular()[:5].fetch_with_posts_count()
    likes = post.likes.count()
    related_tags = post.tags.fetch_with_posts_count()

    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': likes,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }

    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)
    most_popular_posts = Post.objects.popular()[:5].\
        prefetch_authors().\
        prefetch_tags_and_count_posts().\
        fetch_with_comments_count()
    most_popular_tags = Tag.objects.popular()[:5].fetch_with_posts_count()
    related_posts = tag.posts.popular()[:20].\
        prefetch_authors().\
        prefetch_tags_and_count_posts().\
        fetch_with_comments_count()

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }

    return render(request, 'posts-list.html', context)


def contacts(request):
    return render(request, 'contacts.html', {})
