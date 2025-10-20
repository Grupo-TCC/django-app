from django.db import models
from django.conf import settings
from .community_models import Community

class CommunityMessage(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField(help_text="Texto da mensagem.", blank=True)
    pdf = models.FileField(upload_to='community_messages/', blank=True, null=True, verbose_name="Arquivo", help_text="Arquivos permitidos: PDF, imagens, documentos Word, arquivos de texto")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.fullname}: {self.body[:30]}{' [Arquivo]' if self.pdf else ''}"
    
    @property
    def has_file(self):
        """Check if message has a file attachment"""
        return bool(self.pdf)
    
    @property
    def filename(self):
        """Get the original filename of the attachment"""
        if self.pdf:
            import os
            return os.path.basename(self.pdf.name)
        return None
    
    @property
    def file_type(self):
        """Get the file type/extension"""
        if self.pdf:
            import os
            return os.path.splitext(self.pdf.name)[1].lower()
        return None
    
    @property
    def pdf_size(self):
        """Get PDF file size in human readable format"""
        if self.pdf and hasattr(self.pdf, 'file'):
            try:
                size = self.pdf.size
                # Convert bytes to human readable format
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size < 1024.0:
                        return f"{size:.1f} {unit}"
                    size /= 1024.0
                return f"{size:.1f} TB"
            except (OSError, AttributeError):
                return "Unknown size"
        return None
    
    def get_pdf_url(self):
        """Get the URL for the PDF file"""
        if self.pdf:
            return self.pdf.url
        return None
