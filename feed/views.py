from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Post, Comment
from user.models import User, Follow
from .forms import PostForm, CommunityForm
from django.views.decorators.http import require_POST, require_http_methods
from django.db.models import Count, Case, When, Value, IntegerField
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from feed.article_models import Article
from django.db.models import Q
from .community_models import Community
from .community_detail_view import community_detail
#from user.forms import InnovatorVerificationForm    

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
    
def conexao(request):
    query = request.GET.get('q', '').strip()
    users = User.objects.filter(is_active=True, email_verified=True).exclude(id=request.user.id)
    if query:
        users = users.filter(fullname__icontains=query)
    following_ids = set(
        request.user.following.values_list("following_id", flat=True)
    )
    return render(request, "feed/conexao.html", {
        "users": users,
        "following_ids": following_ids,
        "search_query": query,
    })
    
@login_required
def toggle_follow(request, user_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")

    target_user = get_object_or_404(User, pk=user_id)
    user = request.user

    # Prevent self-follow
    if user == target_user:
        return JsonResponse({"success": False, "message": "Você não pode seguir a si mesmo."}, status=400)

    follow_obj, created = Follow.objects.get_or_create(follower=user, following=target_user)

    if not created:  
        # already following → unfollow
        follow_obj.delete()
        is_following = False
    else:
        is_following = True

    # Dados do usuário seguido para atualizar a lista via JS
    user_data = {
        "id": target_user.id,
        "fullname": target_user.fullname,
        "profile_picture_url": target_user.get_profile_picture_url(),
        # Adicione outros campos se necessário
    }

    return JsonResponse({
        "success": True,
        "is_following": is_following,
        "user": user_data,
    })
    

@login_required
def settings_view(request):
    return render(request, "feed/settings.html")

def artigos(request):
    from .forms import ArticleForm
    form = ArticleForm()
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.user = request.user
            article.save()
            return redirect('feed:artigos')
    # Filtering
    query = request.GET.get('q', '').strip()
    articles = Article.objects.select_related('user').order_by('-created_at')
    if query:
        articles = articles.filter(
            Q(user__fullname__icontains=query) |
            Q(title__icontains=query) |
            Q(research_area__icontains=query)
        )
    return render(request, 'feed/artigos.html', {
        'articles': articles,
        'search_query': query,
        'form': form,
    })

@login_required
def verificacao(request):
    
    # form = InnovatorVerificationForm(instance=getattr(request.user, 'innovator_verification', None))
    # if request.method == 'POST':
    #     form = InnovatorVerificationForm(request.POST, request.FILES, instance=getattr(request.user, 'innovator_verification', None))
    #     if form.is_valid():
    #         verification = form.save(commit=False)
    #         verification.user = request.user
    #         verification.save()
    #         return redirect('feed:settings')
    return render(request, 'feed/verificacao.html', {
        # 'title': 'Verificação de Pesquisador',
        # 'description': 'Envie seus documentos para verificação.',
        # 'form_title': 'Formulário de Verificação',
        # 'form': form,
    })

# View para página de perfil
def perfil(request):
    return render(request, 'feed/perfil.html')


# Community page: list communities, search, and create modal

@login_required
def community(request):
    query = request.GET.get('q', '').strip()
    communities = Community.objects.all().order_by('-created_at')
    if query:
        communities = communities.filter(name__icontains=query)
    form = CommunityForm()

    # Handle join/leave logic
    join_id = request.GET.get('join')
    leave_id = request.GET.get('leave')
    if request.method == 'POST':
        # Community creation
        if not join_id and not leave_id:
            form = CommunityForm(request.POST, request.FILES)
            if form.is_valid():
                community = form.save(commit=False)
                community.created_by = request.user
                community.save()
                community.members.add(request.user)
                return redirect('feed:community')
        # Join community
        elif join_id:
            community = get_object_or_404(Community, id=join_id)
            community.members.add(request.user)
            return redirect('feed:community')
        # Leave community
        elif leave_id:
            community = get_object_or_404(Community, id=leave_id)
            community.members.remove(request.user)
            return redirect('feed:community')

    return render(request, "feed/community.html", {
        "communities": communities,
        "form": form,
        "search_query": query,
    })

# def conexao_list(request):
#     queryset = Conexao.objects.all()
#     search_query = request.GET.get('q', '')
#     search_type = request.GET.get('search_type', '')
    
#     if search_query:
#         if search_type == 'name_only' or 'conexao' in request.path:
#             # Search only by name for conexao page
#             queryset = queryset.filter(
#                 Q(name__icontains=search_query)
#             )
#         else:
#             # Default search (multiple fields)
#             queryset = queryset.filter(
#                 Q(name__icontains=search_query) |
#                 Q(description__icontains=search_query)
#             )
    
#     context = {
#         'conexoes': queryset,
#         'search_query': search_query,
#     }
#     return render(request, 'conexao/list.html', context)

# def artigo_list(request):
#     queryset = Artigo.objects.all()
#     search_query = request.GET.get('q', '')
#     search_type = request.GET.get('search_type', '')
    
#     if search_query:
#         if search_type == 'multiple_fields' or 'artigo' in request.path:
#             # Search by name, title, research area for artigos
#             queryset = queryset.filter(
#                 Q(author__name__icontains=search_query) |
#                 Q(title__icontains=search_query) |
#                 Q(research_area__icontains=search_query) |
#                 Q(abstract__icontains=search_query)
#             )
#         else:
#             # Default search
#             queryset = queryset.filter(
#                 Q(title__icontains=search_query) |
#                 Q(author__name__icontains=search_query)
#             )
    
#     context = {
#         'artigos': queryset,
#         'search_query': search_query,
#     }
#     return render(request, 'artigo/list.html', context)

