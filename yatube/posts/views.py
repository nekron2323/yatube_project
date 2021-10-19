from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import Group, Post
# Create your views here.


def index(request):
    posts = Post.objects.order_by('-pub_date')[:10]
    context = {
        'posts': posts
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):    
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]    
    context = {
        'title': slug,
        'posts': posts,
    }
    return render(request, template, context)
