from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from feed.article_models import Article

@login_required
@require_POST
def delete_article(request, article_id):
    article = get_object_or_404(Article, id=article_id, user=request.user)
    article.delete()
    return redirect('feed:perfil')
