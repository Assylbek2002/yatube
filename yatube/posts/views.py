from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Comment
from .forms import PostForm, CommentForm
from django.core.paginator import Paginator


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, 'page': page, 'paginator': paginator})


def index(request):
    posts = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    """Поскольку в шаблоне форма по умолчанию будет отправляться на тот же адрес,
    то представление обрабатывает сразу да типа запросов GET и POST."""
    if request.method == "POST":
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.pub_date = datetime.now()
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, 'new_post.html', {'form': form})


@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=user)
    count_posts = len(user_posts)
    paginator = Paginator(user_posts, 5)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "profile.html", {'user': user, 'page': page, 'count': count_posts})


@login_required
def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=user)
    count_posts = len(user_posts)
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm()
    items = post.comments.all()
    return render(request, "post.html", {'count': count_posts, 'post': post, 'current_user': user,
                                         'form': form, 'items': items})


@login_required
def post_edit(request, username, post_id):
    user = get_object_or_404(User, username=username) # get user --- terminator
    post = Post.objects.get(author=user, id=post_id) # get post
    if user == request.user:
        if request.method == "POST":
            form = PostForm(request.POST, instance=post, files=request.FILES or None)
            if form.is_valid():
                post = form.save(commit=False)
                post.save()
                return redirect(f'/{username}/')
        else:
            form = PostForm(instance=post, files=request.FILES or None)
        return render(request, "post_edit.html", {"post": post, 'form': form})
    else:
        return redirect(f"/{username}/{post_id}")


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    items = post.comments.all()
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.created = datetime.now()
            comment.save()
            return redirect(f"/{username}/{post_id}/")
    else:
        form = CommentForm()
    return render(request, "post.html", {'form': form, 'items': items})
