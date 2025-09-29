from django.db import models
from django.conf import settings
from .article_models import Article

class ArticleAccess(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    has_access = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'article')
        verbose_name = 'Acesso a Artigo Pago'
        verbose_name_plural = 'Acessos a Artigos Pagos'

    def __str__(self):
        return f"{self.user.fullname} - {self.article.title} ({'Acesso' if self.has_access else 'Sem acesso'})"

class ArticleAccessRequest(models.Model):
    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    article = models.ForeignKey('feed.Article', on_delete=models.CASCADE)
    slip = models.FileField(upload_to='article_access_slips/')
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Pedido de Acesso a Artigo'
        verbose_name_plural = 'Pedidos de Acesso a Artigos'
        unique_together = ('user', 'article')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # If approved, grant access
        if self.approved:
            from .article_access_models import ArticleAccess
            ArticleAccess.objects.update_or_create(
                user=self.user,
                article=self.article,
                defaults={'has_access': True}
            )

    def __str__(self):
        return f"{self.user.fullname} - {self.article.title} ({'Aprovado' if self.approved else 'Pendente'})"
