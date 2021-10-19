from django.http.response import HttpResponse
from django.shortcuts import render
from .models import Post
# Create your views here.


def index(request):
    posts = Post.objects.order_by('-pub_date')[:10]
    context = {
        'posts': posts
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    text = 'Здесь будет информация о группах проекта Yatube'
    context = {
        'title': slug,
        'text': text,
    }
    return render(request, template, context)
