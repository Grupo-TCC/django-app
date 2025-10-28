from django.db import models
from django.conf import settings
import os


class LegacyMediaPost(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Imagem'),
        ('video', 'Vídeo'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="legacy_media_posts")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição")
    media_file = models.FileField(upload_to='media_posts/', verbose_name="Arquivo de Mídia")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, verbose_name="Tipo de Mídia")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # Make this abstract to avoid conflicts
        ordering = ['-created_at']
        verbose_name = "Legacy Post de Mídia"
        verbose_name_plural = "Legacy Posts de Mídia"

    def __str__(self):
        return f"{self.title} - {self.user.fullname}"

    def save(self, *args, **kwargs):
        # Auto-detect media type based on file extension
        if self.media_file:
            file_extension = os.path.splitext(self.media_file.name)[1].lower()
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']
            
            if file_extension in image_extensions:
                self.media_type = 'image'
            elif file_extension in video_extensions:
                self.media_type = 'video'
        
        super().save(*args, **kwargs)

    @property
    def is_image(self):
        return self.media_type == 'image'

    @property
    def is_video(self):
        return self.media_type == 'video'

    def get_media_type_display(self):
        return dict(self.MEDIA_TYPE_CHOICES).get(self.media_type, 'Desconhecido')

    def get_file_size(self):
        """Return formatted file size"""
        if self.media_file:
            try:
                size = self.media_file.size
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size < 1024.0:
                        return f"{size:.1f} {unit}"
                    size /= 1024.0
                return f"{size:.1f} TB"
            except:
                return "Tamanho desconhecido"
        return "Sem arquivo"

    def get_file_url(self):
        """Return the URL of the media file"""
        if self.media_file:
            # Check if the file actually exists on disk
            try:
                if self.media_file.storage.exists(self.media_file.name):
                    return self.media_file.url
                else:
                    # File doesn't exist (maybe moved to iCloud), return None
                    return None
            except:
                # Any error accessing the file, return None
                return None
        return None