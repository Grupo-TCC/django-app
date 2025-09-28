from django.db import models
from django.conf import settings
from .community_models import Community

class CommunityMessage(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField(help_text="Texto da mensagem.", blank=True)
    pdf = models.FileField(upload_to='community_messages/pdfs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.fullname}: {self.body[:30]}{' [PDF]' if self.pdf else ''}"
