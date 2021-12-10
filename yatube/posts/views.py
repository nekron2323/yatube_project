from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .settings import CACHE_TIME, PAGINATOR_NUM_PAGES


def get_paginator_page(request, items):
    paginator = Paginator(items, PAGINATOR_NUM_PAGES)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(CACHE_TIME)
def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': get_paginator_page(request, Post.objects.all())
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': get_paginator_page(request, group.posts.all()),
        'is_group': True
    })


def profile(request, username):
    author = User.objects.get(username=username)
    is_following = (
        request.user.is_authenticated
        and author != request.user
        and author.following.filter(user=request.user).exists()
    )
    return render(request, 'posts/profile.html', {
        'page_obj': get_paginator_page(request, author.posts.all()),
        'author': author,
        'following': is_following
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'form': form,
        'is_post_detail': True
    })


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect('posts:profile', username=request.user)


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {
            'is_edit': True,
            'form': form
        })
    form.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    return render(request, 'posts/follow.html', {
        'page_obj': get_paginator_page(
            request,
            Post.objects.filter(author__following__user=request.user)
        )
    })


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    if not (author == request.user
            or author.following.filter(user=request.user).exists()):
        Follow.objects.create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow, user=request.user,
        author__username=username
    ).delete()
    return redirect('posts:profile', username)
