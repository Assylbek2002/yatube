from django.shortcuts import render, get_object_or_404
from .models import Post, Group


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    return render(request, "group.html", {"group": group, "posts": posts})


def index(request):
    posts = Post.objects.all()
    context = {"posts": posts}
    return render(request, "index.html", context)