from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect, reverse
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, 'page': page, 'paginator': paginator})


@cache_page(500, key_prefix="index_page")
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
    other_user = request.user
    user_posts = Post.objects.filter(author=user)
    count_posts = len(user_posts)
    paginator = Paginator(user_posts, 5)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    followers = user.following.count()
    follows = user.follower.count()
    following = False
    subscribers = user.following.all()
    following_users = User.objects.filter(id__in=subscribers.values_list('user'))
    if request.user in following_users:
        following = True
    return render(request, "profile.html", {'user': user, 'page': page, 'count': count_posts, 'other': other_user,
                                            "followers": followers, "following": following, 'follows': follows})


@login_required
def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = CommentForm()
    items = post.comments.all()
    return render(request, "post.html", {'post': post, 'form': form, 'items': items})


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


@login_required
def follow_index(request):
    subscribers = request.user.follower.all()
    posts = Post.objects.filter(author__in=subscribers.values_list('author').distinct())
    paginator = Paginator(posts, 5)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {"page": page})


@login_required
def profile_follow(request, username):
    """Подписка на автора"""
    author = get_object_or_404(User, username=username)
    Follow.objects.create(author=author, user=request.user)
    return redirect(f"/{username}/")


@login_required
def profile_unfollow(request, username):
    """Отписка от автора"""
    author = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, author=author, user=request.user)
    follow.delete()
    return redirect(f"/{username}/")


