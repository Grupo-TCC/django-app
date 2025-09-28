from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .community_models import Community
from user.models import User
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db.models import Q
from .community_message_models import CommunityMessage

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
        message = request.POST.get('message', '').strip()
        pdf_file = request.FILES.get('pdf')
        if pdf_file and pdf_file.content_type != 'application/pdf':
            # Only allow PDF files
            return render(request, 'feed/community_detail.html', {
                'community': community,
                'messages': community.messages.select_related('user').all(),
                'possible_invites': possible_invites,
                'error': 'Apenas arquivos PDF são permitidos.'
            })
        if message or pdf_file:
            CommunityMessage.objects.create(
                community=community,
                user=request.user,
                body=message,
                pdf=pdf_file if pdf_file else None
            )
        return redirect('feed:community_detail', community_id=community.id)

    # Fetch messages for this community
    messages = community.messages.select_related('user').all()
    # For inviting members, get users the current user follows who are not already members
    following_ids = request.user.following.values_list('following_id', flat=True)
    possible_invites = User.objects.filter(id__in=following_ids).exclude(id__in=community.members.values_list('id', flat=True))

    return render(request, 'feed/community_detail.html', {
        'community': community,
        'messages': messages,
        'possible_invites': possible_invites,
    })
