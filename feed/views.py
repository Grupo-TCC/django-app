from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Post
from .forms import PostForm
from django.views.decorators.http import require_POST

# Create your views here.

@login_required(login_url='register')
def home(request):
    posts = (
    Post.objects
    .select_related('user')
    .prefetch_related('likes')
    .order_by('-created_at')
)

    # set of post IDs the current user already liked (efficient)
    liked_ids = set(
        request.user.liked_posts.values_list('id', flat=True)
    )
    form = PostForm() if request.user.user_type == 'In' else None
    
    if request.method == 'POST' and request.user.user_type == 'In':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('feed:home')

    
    return render(request, 'feed/home.html', {
        'form': form,
        'posts': posts,
        'liked_ids': liked_ids
    })

@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    # faster existence check than "user in post.likes.all()"
    already_liked = post.likes.filter(pk=request.user.pk).exists()

    if already_liked:
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    return JsonResponse({
        "liked": liked,
        "count": post.likes.count(),
        "post_id": post.pk,
    })