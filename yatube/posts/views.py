from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Comment, Follow
from .utils import paginator_create


@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    page_obj, page_number = paginator_create(request, post_list)
    context = {
        'page_obj': page_obj,
        'page_index': page_number,
        'index': True
    }
    return render(request, 'posts/index.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_profile = author.posts.all()
    page_obj, page_number = paginator_create(request, posts_profile)
    following = False
    res = posts_profile.filter(author__following__user=author)
    if not res.exists():
        following = True

    context = {
        'page_obj': page_obj,
        'page_number': page_number,
        'author': author,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comment_form = CommentForm()
    comments = Comment.objects.filter(post=post_id)
    return render(request, 'posts/post_detail.html', {"post": post,
                                                      "form": comment_form,
                                                      "comments": comments})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_groups = group.posts.all()
    page_obj, _ = paginator_create(request, posts_groups)
    context = {
        'page_obj': page_obj,
        'group': group

    }
    return render(request, "posts/group_list.html", context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/post_create.html',
                      {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('main:profile', post.author)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('main:post_detail', post_id=post_id)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('main:post_detail', post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('main:post_detail', post_id)
    context = {'form': form,
               'is_edit': True,
               'post_id': post_id}
    return render(request, 'posts/post_create.html', context)


@login_required
def follow_index(request):
    cur_user = get_object_or_404(User, id=request.user.id)
    post_list = (
        Post.objects.filter(author__following__user=request.user)
        .select_related('group')
    )
    page_obj, page_number = paginator_create(request, post_list)
    context = {
        'page_obj': page_obj,
        'page_index': page_number,
        'cur_user': cur_user,
        'follow': True
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    curr_user = request.user
    if request.user != author:
        follow_ex = author
        check_user_in_follow = (Follow.objects.filter(user=curr_user,
                                author=follow_ex.id))
        if not check_user_in_follow.exists():
            Follow.objects.create(user=curr_user, author=follow_ex)

    return redirect('main:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    curr_user = request.user
    if request.user != author:
        follow_ex = author
        check_user_in_follow = (Follow.objects.filter(user=curr_user,
                                author=follow_ex.id))
        if check_user_in_follow.exists():
            Follow.objects.filter(user=curr_user, author=follow_ex).delete()
    return redirect('main:profile', username)
