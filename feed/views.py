# Página de mensagens
from django.shortcuts import render, redirect

from django.db import models
from django.contrib.auth.decorators import login_required

# Simple test view for video functionality
def video_test(request):
    return render(request, 'video-test.html')

# Debug view for video auto-pause functionality
def video_debug(request):
    return render(request, 'video-debug.html')

@login_required
def mensagens(request):
    from .models import Message
    following_users = [f.following for f in Follow.objects.filter(follower=request.user).select_related('following')]
    conversation_data = []
    selected_user_id = request.GET.get('user')
    selected_user = None
    chat_messages = []
    for user in following_users:
        last_msg = Message.objects.filter(
            (models.Q(sender=request.user, recipient=user) | models.Q(sender=user, recipient=request.user))
        ).order_by('-created_at').first()
        conversation_data.append({
            'id': user.id,
            'fullname': user.fullname,
            'profile_picture_url': user.get_profile_picture_url(),
            'last_message': last_msg.body if last_msg else '',
            'last_sender_id': last_msg.sender_id if last_msg else None,
            'last_message_time': last_msg.created_at if last_msg else None,
        })
        if selected_user_id and str(user.id) == str(selected_user_id):
            selected_user = user
            chat_messages = Message.objects.filter(
                (models.Q(sender=request.user, recipient=user) | models.Q(sender=user, recipient=request.user))
            ).order_by('created_at')
    # Order by last_message_time desc, None last
    import datetime
    import pytz
    def to_naive_utc(dt):
        if dt is None:
            return datetime.datetime(1970, 1, 1)
        if dt.tzinfo is not None:
            return dt.astimezone(pytz.UTC).replace(tzinfo=None)
        return dt
    conversation_data.sort(key=lambda c: to_naive_utc(c['last_message_time']), reverse=True)
    return render(request, 'feed/mensagens.html', {
        'conversations': conversation_data,
        'selected_user': selected_user,
        'chat_messages': chat_messages,
    })
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.contrib import messages

from user.models import User, Follow
from .forms import CommunityForm, MediaPostForm
from .models import MediaPost


from django.conf import settings
from django.core.files.storage import FileSystemStorage
from feed.article_models import Article
from django.db.models import Q
from .community_models import Community
from .community_detail_view import community_detail
from .article_access_models import ArticleAccess
from user.forms_settings import UserResearchInstitutionForm
from .constants import RESEARCH_AREA_CHOICES
from feed.article_models import Article
from user.models import Follow
from feed.community_models import Community
from .utils import get_regular_users_except

#from user.forms import InnovatorVerificationForm    

# Create your views here.

def conexao(request):
    query = request.GET.get('q', '').strip()
    users = get_regular_users_except(request.user)
    if query:
        users = users.filter(fullname__icontains=query)
    following_ids = set(
        request.user.following.values_list("following_id", flat=True)
    )
    
    # Top 5 users with most recent messages (for sidebar - consistent with other pages)
    from .models import Message
    from user.models import Follow
    
    user = request.user if request.user.is_authenticated else None
    top_message_users = []
    
    if user:
        # Get users the current user follows
        following_users = [f.following for f in Follow.objects.filter(follower=user).select_related('following')]
        conversation_data = []
        
        for u in following_users:
            last_msg = Message.objects.filter(
                (Q(sender=user, recipient=u) | Q(sender=u, recipient=user))
            ).order_by('-created_at').first()
            conversation_data.append({
                'user': u,
                'last_message_time': last_msg.created_at if last_msg else None,
            })
        
        import datetime
        import pytz
        
        def to_naive_utc(dt):
            if dt is None:
                return datetime.datetime(1970, 1, 1)
            if dt.tzinfo is not None:
                return dt.astimezone(pytz.UTC).replace(tzinfo=None)
            return dt
        
        conversation_data.sort(key=lambda c: to_naive_utc(c['last_message_time']), reverse=True)
        top_message_users = [c['user'] for c in conversation_data[:5]]
    
    return render(request, "feed/conexao.html", {
        "users": users,
        "following_ids": following_ids,
        "search_query": query,
        "top_message_users": top_message_users,
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

@login_required
def settings_view(request):
    user = request.user
    area_success = None
    form = UserResearchInstitutionForm(request.POST or None, instance=user)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            area_success = True
            # Re-instantiate the form with the updated user instance
            form = UserResearchInstitutionForm(instance=user)
    return render(request, "feed/settings.html", {
        "area_success": area_success,
        "area_form": form,
    })

@login_required
def artigos(request):
    from .forms import ArticleForm
    form = ArticleForm()
    
    if request.method == 'POST':
        # Handle normal article upload
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.user = request.user
            article.save()
            return redirect('feed:artigos')
    
    # Filtering
    query = request.GET.get('q', '').strip()
    articles = Article.objects.select_related('user').order_by('title')
    if query:
        articles = articles.filter(
            Q(user__fullname__icontains=query) |
            Q(title__icontains=query) |
            Q(research_area__icontains=query)
        )
    
    user = request.user if request.user.is_authenticated else None
    # Top 5 users with most recent messages (for sidebar)
    from .models import Message
    from user.models import Follow
    top_message_users = []
    if user:
        # Get users the current user follows
        following_users = [f.following for f in Follow.objects.filter(follower=user).select_related('following')]
        conversation_data = []
        for u in following_users:
            last_msg = Message.objects.filter(
                (Q(sender=user, recipient=u) | Q(sender=u, recipient=user))
            ).order_by('-created_at').first()
            conversation_data.append({
                'user': u,
                'last_message_time': last_msg.created_at if last_msg else None,
            })
        import datetime
        import pytz
        def to_naive_utc(dt):
            if dt is None:
                return datetime.datetime(1970, 1, 1)
            if dt.tzinfo is not None:
                return dt.astimezone(pytz.UTC).replace(tzinfo=None)
            return dt
        conversation_data.sort(key=lambda c: to_naive_utc(c['last_message_time']), reverse=True)
        top_message_users = [c['user'] for c in conversation_data[:5]]
    return render(request, 'feed/artigos.html', {
        'articles': articles,
        'search_query': query,
        'form': form,
        'top_message_users': top_message_users,
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
# Accepts optional user_id for viewing other users' profiles

def perfil(request, user_id=None):
    from .models import Product
    
    if user_id is not None:
        profile_user = get_object_or_404(User, pk=user_id)
    else:
        profile_user = request.user

    # Salvar edição do perfil apenas para o próprio usuário
    if request.method == 'POST' and user_id is None:
        research_area = request.POST.get('research_area', '').strip()
        institution = request.POST.get('institution', '').strip()
        profile_user.research_area = research_area
        profile_user.institution = institution
        profile_user.save()
        return redirect('feed:perfil')

    # Get all user content
    user_articles = Article.objects.filter(user=profile_user).order_by('-created_at')
    user_translations = MediaPost.objects.filter(user=profile_user).order_by('-created_at')
    user_products = Product.objects.filter(user=profile_user).order_by('-created_at')
    
    following_users = [f.following for f in Follow.objects.filter(follower=profile_user).select_related('following')]
    joined_communities = Community.objects.filter(members=profile_user).order_by('name')
    return render(request, 'feed/perfil.html', {
        'user_articles': user_articles,
        'user_translations': user_translations,
        'user_products': user_products,
        'following_users': following_users,
        'joined_communities': joined_communities,
        'profile_user': profile_user,
    })


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
            # If form is invalid, it will be passed to the template with errors
            else:
                # Log form errors for debugging
                print(f"Community form errors: {form.errors}")
                if hasattr(form, 'non_field_errors'):
                    print(f"Non-field errors: {form.non_field_errors()}")
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

    user_communities = communities.filter(members=request.user)
    return render(request, "feed/community.html", {
        "communities": communities,
        "user_communities": user_communities,
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


@login_required
def media_post(request):
    """View for media posts (photos and videos) - Tradução de Conhecimento"""
    search_query = request.GET.get('q', '').strip()
    
    # Filter media posts based on search query
    media_posts = MediaPost.objects.all().select_related('user').order_by('-created_at')
    if search_query:
        media_posts = media_posts.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(user__fullname__icontains=search_query) |
            Q(user__research_area__icontains=search_query)
        )
    
    # Add access information and like status for each media post
    for media in media_posts:
        media.user_has_access = media.user_has_access(request.user)
        media.is_liked_by_user = media.is_liked_by(request.user)
    
    # Top 5 users with most recent messages (for sidebar - consistent with other pages)
    from .models import Message
    from user.models import Follow
    
    user = request.user if request.user.is_authenticated else None
    top_message_users = []
    
    if user:
        # Get users the current user follows
        following_users = [f.following for f in Follow.objects.filter(follower=user).select_related('following')]
        conversation_data = []
        
        for u in following_users:
            last_msg = Message.objects.filter(
                (Q(sender=user, recipient=u) | Q(sender=u, recipient=user))
            ).order_by('-created_at').first()
            conversation_data.append({
                'user': u,
                'last_message_time': last_msg.created_at if last_msg else None,
            })
        
        import datetime
        import pytz
        
        def to_naive_utc(dt):
            if dt is None:
                return datetime.datetime(1970, 1, 1)
            if dt.tzinfo is not None:
                return dt.astimezone(pytz.UTC).replace(tzinfo=None)
            return dt
        
        conversation_data.sort(key=lambda c: to_naive_utc(c['last_message_time']), reverse=True)
        top_message_users = [c['user'] for c in conversation_data[:5]]
    
    form = MediaPostForm(user=request.user)
    
    if request.method == 'POST':
        form = MediaPostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            media_post = form.save()
            return redirect('feed:media_post')
        else:
            # Log form errors for debugging
            print(f"MediaPost form errors: {form.errors}")
    
    context = {
        'media_posts': media_posts,
        'form': form,
        'search_query': search_query,
        'top_message_users': top_message_users,
    }
    return render(request, 'feed/traducao.html', context)


@login_required
def request_media_access(request, media_id):
    """Handle access requests for paid media content with payment slip upload"""
    if request.method != 'POST':
        return redirect('feed:media_post')
    
    try:
        from .models import MediaAccessRequest
        media_post = get_object_or_404(MediaPost, id=media_id)
        
        # Check if user already has access
        if media_post.user_has_access(request.user):
            messages.error(request, 'Você já tem acesso a este conteúdo')
            return redirect('feed:media_post')
        
        # Check if user is the owner
        if media_post.user == request.user:
            messages.error(request, 'Você é o proprietário deste conteúdo')
            return redirect('feed:media_post')
        
        # Check if media post is not paid
        if media_post.is_free:
            messages.error(request, 'Este conteúdo é gratuito')
            return redirect('feed:media_post')
        
        # Check if user already has a pending request
        existing_request = MediaAccessRequest.objects.filter(
            user=request.user, 
            media_post=media_post
        ).first()
        
        if existing_request:
            if existing_request.approved:
                messages.info(request, 'Sua solicitação já foi aprovada!')
            else:
                messages.info(request, 'Você já possui uma solicitação pendente para este conteúdo.')
            return redirect('feed:media_post')
        
        # Handle file upload
        payment_slip = request.FILES.get('payment_slip')
        if not payment_slip:
            messages.error(request, 'É necessário enviar o comprovante de pagamento.')
            return redirect('feed:media_post')
        
        # Create the access request
        MediaAccessRequest.objects.create(
            user=request.user,
            media_post=media_post,
            payment_slip=payment_slip
        )
        
        messages.success(request, 'Solicitação de acesso enviada com sucesso! Aguarde a aprovação.')
        return redirect('feed:media_post')
        
    except Exception as e:
        messages.error(request, f'Erro ao processar solicitação: {str(e)}')
        return redirect('feed:media_post')


@login_required
def toggle_media_like(request, media_id):
    """Toggle like for a media post"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        from .models import MediaLike
        media_post = get_object_or_404(MediaPost, id=media_id)
        
        # Check if user already liked this post
        like, created = MediaLike.objects.get_or_create(
            user=request.user,
            media_post=media_post
        )
        
        if created:
            # Like was created
            liked = True
        else:
            # Like already existed, so remove it (unlike)
            like.delete()
            liked = False
        
        # Get updated like count
        like_count = media_post.like_count
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'like_count': like_count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def add_media_comment(request, media_id):
    """Add a comment to a media post"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        import json
        from .models import MediaComment
        
        data = json.loads(request.body)
        comment_body = data.get('body', '').strip()
        
        if not comment_body:
            return JsonResponse({'success': False, 'error': 'Comentário não pode estar vazio'})
        
        media_post = get_object_or_404(MediaPost, id=media_id)
        
        # Create new comment
        comment = MediaComment.objects.create(
            user=request.user,
            media_post=media_post,
            body=comment_body
        )
        
        # Get updated comment count
        comment_count = media_post.comment_count
        
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'body': comment.body,
                'user_name': comment.user.fullname,
                'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M'),
            },
            'comment_count': comment_count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_media_comments(request, media_id):
    """Get comments for a media post"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        from .models import MediaComment
        media_post = get_object_or_404(MediaPost, id=media_id)
        
        # Get comments for this media post
        comments = MediaComment.objects.filter(media_post=media_post).select_related('user').order_by('-created_at')
        
        comments_data = []
        for comment in comments:
            comments_data.append({
                'id': comment.id,
                'body': comment.body,
                'user_name': comment.user.fullname,
                'user_profile_picture': comment.user.get_profile_picture_url(),
                'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M'),
                'is_owner': comment.user == request.user,
            })
        
        return JsonResponse({
            'success': True,
            'comments': comments_data,
            'comment_count': len(comments_data)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def produtos(request):
    from .forms import ProductForm
    from .models import Product
    
    form = ProductForm()
    
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            return redirect('feed:produtos')
    
    # Filtering
    query = request.GET.get('q', '').strip()
    area_filter = request.GET.get('area', '').strip()
    
    products = Product.objects.select_related('user').order_by('-created_at')
    
    if query:
        products = products.filter(
            Q(user__fullname__icontains=query) |
            Q(titulo__icontains=query) |
            Q(descricao__icontains=query)
        )
    
    if area_filter:
        products = products.filter(area_pesquisa=area_filter)
    
    # Get research areas for filter dropdown
    research_areas = RESEARCH_AREA_CHOICES
    
    # Top 5 users with most recent messages (for sidebar - consistent with other pages)
    from .models import Message
    from user.models import Follow
    
    user = request.user if request.user.is_authenticated else None
    top_message_users = []
    
    if user:
        # Get users the current user follows
        following_users = [f.following for f in Follow.objects.filter(follower=user).select_related('following')]
        conversation_data = []
        
        for u in following_users:
            last_msg = Message.objects.filter(
                (Q(sender=user, recipient=u) | Q(sender=u, recipient=user))
            ).order_by('-created_at').first()
            conversation_data.append({
                'user': u,
                'last_message_time': last_msg.created_at if last_msg else None,
            })
        
        import datetime
        import pytz
        
        def to_naive_utc(dt):
            if dt is None:
                return datetime.datetime(1970, 1, 1)
            if dt.tzinfo is not None:
                return dt.astimezone(pytz.UTC).replace(tzinfo=None)
            return dt
        
        conversation_data.sort(key=lambda c: to_naive_utc(c['last_message_time']), reverse=True)
        top_message_users = [c['user'] for c in conversation_data[:5]]
    
    return render(request, 'feed/produtos.html', {
        'products': products,
        'search_query': query,
        'area_filter': area_filter,
        'research_areas': research_areas,
        'form': form,
        'top_message_users': top_message_users,
    })

