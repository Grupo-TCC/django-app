from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Post, Comment
from user.models import User, Follow
from .forms import PostForm
from django.views.decorators.http import require_POST, require_http_methods
from django.db.models import Count, Case, When, Value, IntegerField

# Create your views here.

@login_required(login_url='register')
def home(request):
    following_ids = request.user.following.values_list("following_id", flat=True)

    posts = (
    Post.objects
    .select_related('user')
    .prefetch_related('likes', 'comments__user')
    .annotate(priority=Case(
                # priority=0 if post is by followed user or self
                When(user__in=list(following_ids) + [request.user.id], then=Value(0)),
                # priority=1 otherwise
                default=Value(1),
                output_field=IntegerField(),
            ),comment_count=Count('comments'))
    .order_by('priority', '-created_at')
)

    # set of post IDs the current user already liked (efficient)
    liked_ids = set(
        request.user.liked_posts.values_list('id', flat=True)
    )
    form = PostForm() 
    
    if request.method == 'POST' :
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
    
@login_required
@require_http_methods(["GET", "POST"])
def comments_api(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == "GET":
        data = [{
            "id": c.id,
            "user_fullname": c.user.fullname,
            "user_title": getattr(getattr(c.user, "innovator_verification", None), "title", ""),
            "body": c.body,
            "created": c.created_at.strftime("%d %b %Y, %H:%M"),
        } for c in post.comments.select_related('user')]
        return JsonResponse({"comments": data, "count": post.comments.count()})

    # POST: create comment
    body = (request.POST.get("body") or "").strip()
    if not body:
        return JsonResponse({"success": False, "message": "Escreva um comentário."}, status=400)

    c = Comment.objects.create(post=post, user=request.user, body=body)
    return JsonResponse({
        "success": True,
        "comment": {
            "id": c.id,
            "user_fullname": c.user.fullname,
            "user_title": getattr(getattr(c.user, "innovator_verification", None), "title", ""),
            "body": c.body,
            "created": c.created_at.strftime("%d %b %Y, %H:%M"),
        },
        "count": post.comments.count(),
    })
    
@login_required
def community(request):
    users = User.objects.exclude(id=request.user.id)
    following_ids = set(
        request.user.following.values_list("following_id", flat=True)
    )
    return render(request, "feed/community.html", {
        "users": users,
        "following_ids": following_ids,
    })
    
@login_required
def toggle_follow(request, user_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    target_user = get_object_or_404(User, pk=user_id)
    user = request.user

    # Prevent self-follow
    if user == target_user:
        return JsonResponse({"success": False, "message": "You cannot follow yourself."}, status=400)

    follow_obj, created = Follow.objects.get_or_create(follower=user, following=target_user)

    if not created:  
        # already following → unfollow
        follow_obj.delete()
        is_following = False
    else:
        is_following = True

    return JsonResponse({
        "success": True,
        "is_following": is_following,
        "user_id": target_user.id,
    })
    

@login_required
def settings_view(request):
    return render(request, "feed/settings.html")

