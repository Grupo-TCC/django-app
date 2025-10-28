from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from feed.models import MediaPost

@login_required
@require_POST
def delete_media_post(request, media_id):
    media_post = get_object_or_404(MediaPost, id=media_id, user=request.user)
    media_post.delete()
    return redirect('feed:perfil')