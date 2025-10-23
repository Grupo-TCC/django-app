from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .community_models import Community
from user.models import User
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db.models import Q
from .community_message_models import CommunityMessage
from .utils import get_regular_users

@login_required
def community_detail(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    # Only members can view/post
    if request.user not in community.members.all():
        return HttpResponseForbidden("Você não é membro desta comunidade.")

    # Handle inviting a user to the community
    invite_id = request.GET.get('invite')
    if invite_id:
        user_to_invite = User.objects.filter(id=invite_id).first()
        if user_to_invite:
            community.members.add(user_to_invite)
        return redirect('feed:community_detail', community_id=community.id)

    # Message posting logic
    if request.method == 'POST':
        message_text = request.POST.get('message_text', '').strip()
        message_file = request.FILES.get('message_file')
        
        # Validate file type if provided
        if message_file:
            allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/gif', 
                           'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                           'text/plain']
            if message_file.content_type not in allowed_types:
                return render(request, 'feed/community_detail.html', {
                    'community': community,
                    'community_messages': community.messages.select_related('user').all(),
                    'possible_invites': get_regular_users().filter(
                        id__in=request.user.following.values_list('following_id', flat=True)
                    ).exclude(id__in=community.members.values_list('id', flat=True)),
                    'error': 'Apenas arquivos PDF, imagens, documentos Word e arquivos de texto são permitidos.'
                })
        
        # Create message if there's text or file
        if message_text or message_file:
            CommunityMessage.objects.create(
                community=community,
                user=request.user,
                body=message_text,
                pdf=message_file if message_file else None
            )
        return redirect('feed:community_detail', community_id=community.id)

    # Fetch messages for this community
    messages = community.messages.select_related('user').all()
    
    # Get messages that have files for the files tab
    messages_with_files = messages.filter(pdf__isnull=False).order_by('-created_at')
    
    # For inviting members, get users the current user follows who are not already members
    try:
        following_ids = request.user.following.values_list('following_id', flat=True)
        possible_invites = get_regular_users().filter(
            id__in=following_ids
        ).exclude(id__in=community.members.values_list('id', flat=True))
    except Exception:
        possible_invites = []

    return render(request, 'feed/community_detail.html', {
        'community': community,
        'community_messages': messages,
        'community_files': messages_with_files,
        'possible_invites': possible_invites,
        'profile_user': request.user,
    })
