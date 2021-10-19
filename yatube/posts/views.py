from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.


def index(request):
    print(request)
    return HttpResponse('<h1>Main page</h1>')


def group_posts(request, slug):
    return HttpResponse(f'<h1>Группы постов {slug}</h1>')
