
from django.db import models
from django.conf import settings
from django.utils import timezone
from .constants import RESEARCH_AREA_CHOICES

# ...existing code...

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.body[:30]}"
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
import os

User = get_user_model()


class MediaPost(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Imagem'),
        ('video', 'Vídeo'),
        ('document', 'Documento'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('free', 'Grátis'),
        ('paid', 'Pago'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="media_posts")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição")
    research_area = models.CharField(
        max_length=50, 
        choices=RESEARCH_AREA_CHOICES, 
        verbose_name="Área de Pesquisa",
        default='outros'
    )
    
    # Payment/Access fields
    payment_type = models.CharField(
        max_length=10, 
        choices=PAYMENT_TYPE_CHOICES, 
        default='free',
        verbose_name="Tipo de Pagamento"
    )
    price = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Preço (R$)",
        help_text="Preço para conteúdo pago"
    )
    
    # Link to Article for payment/access control (only for paid content) - DEPRECATED
    article = models.OneToOneField(
        'Article', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="Artigo Associado (Deprecated)",
        help_text="Artigo para controle de acesso pago - será removido"
    )
    # Temporary field for migration compatibility
    media_file = models.FileField(upload_to='media_posts/', null=True, blank=True, verbose_name="Arquivo de Mídia (temp)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Post de Mídia"
        verbose_name_plural = "Posts de Mídia"

    def __str__(self):
        return f"{self.title} - {self.user.fullname}"

    @property
    def has_images(self):
        return self.files.filter(media_type='image').exists()

    @property
    def has_videos(self):
        return self.files.filter(media_type='video').exists()

    @property
    def has_documents(self):
        return self.files.filter(media_type='document').exists()

    @property
    def file_count(self):
        return self.files.count()

    def get_media_types_display(self):
        """Return a string of all media types in this post"""
        types = []
        if self.has_images:
            types.append("Imagens")
        if self.has_videos:
            types.append("Vídeos")
        if self.has_documents:
            types.append("Documentos")
        return " + ".join(types) if types else "Sem arquivos"

    @property
    def is_paid(self):
        return self.payment_type == 'paid'

    @property
    def is_free(self):
        return self.payment_type == 'free'

    def get_media_type_display(self):
        return dict(self.MEDIA_TYPE_CHOICES).get(self.media_type, 'Desconhecido')
    
    def get_research_area_display(self):
        return dict(RESEARCH_AREA_CHOICES).get(self.research_area, 'Outros')



    def user_has_access(self, user):
        """Check if user has access to this media post"""
        if self.is_free:
            return True
        if self.user == user:  # Owner always has access
            return True
        if not user.is_authenticated:  # Anonymous users don't have access to paid content
            return False
        # Check if user has purchased access through MediaAccess system
        return MediaAccess.objects.filter(user=user, media_post=self, has_access=True).exists()

    @property
    def like_count(self):
        """Return the number of likes for this media post"""
        return self.likes.count()

    @property
    def comment_count(self):
        """Return the number of comments for this media post"""
        return self.comments.count()

    def is_liked_by(self, user):
        """Check if user has liked this media post"""
        if user.is_authenticated:
            return self.likes.filter(user=user).exists()
        return False





class MediaFile(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Imagem'),
        ('video', 'Vídeo'),
        ('document', 'Documento'),
    ]
    
    media_post = models.ForeignKey(MediaPost, on_delete=models.CASCADE, related_name="files")
    media_file = models.FileField(upload_to='media_posts/', verbose_name="Arquivo de Mídia")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, verbose_name="Tipo de Mídia")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Arquivo de Mídia"
        verbose_name_plural = "Arquivos de Mídia"

    def __str__(self):
        return f"{self.media_post.title} - {self.get_media_type_display()}"

    def save(self, *args, **kwargs):
        # Auto-detect media type based on file extension
        if self.media_file:
            file_extension = os.path.splitext(self.media_file.name)[1].lower()
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']
            document_extensions = ['.pdf', '.pptx', '.ppt']
            
            if file_extension in image_extensions:
                self.media_type = 'image'
            elif file_extension in video_extensions:
                self.media_type = 'video'
            elif file_extension in document_extensions:
                self.media_type = 'document'
        
        super().save(*args, **kwargs)

    @property
    def is_image(self):
        return self.media_type == 'image'

    @property
    def is_video(self):
        return self.media_type == 'video'

    @property
    def is_document(self):
        return self.media_type == 'document'

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
        """Return the URL of the media file if it exists"""
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

    def should_block_content(self, user):
        """Check if this specific file should be blocked for user"""
        # Only block PDF/PPTX files for paid posts
        if self.media_post.is_free:
            return False
        if self.media_post.user == user:  # Owner always has access
            return False
        if not self.is_document:  # Only block documents
            return False
        # Check if user has purchased access through Article system
        return not self.media_post.user_has_access(user)


class MediaLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="media_likes")
    media_post = models.ForeignKey(MediaPost, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Curtida de Mídia"
        verbose_name_plural = "Curtidas de Mídia"
        unique_together = ['user', 'media_post']  # One like per user per media post

    def __str__(self):
        return f"{self.user.fullname} liked {self.media_post.title}"


class MediaComment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="media_comments")
    media_post = models.ForeignKey(MediaPost, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField(verbose_name="Comentário")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Comentário de Mídia"
        verbose_name_plural = "Comentários de Mídia"

    def __str__(self):
        return f"{self.user.fullname} commented on {self.media_post.title}: {self.body[:50]}..."


class MediaAccess(models.Model):
    """Model to track user access to paid media posts"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    media_post = models.ForeignKey(MediaPost, on_delete=models.CASCADE)
    has_access = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'media_post')
        verbose_name = 'Acesso a Mídia Paga'
        verbose_name_plural = 'Acessos a Mídias Pagas'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.fullname} - {self.media_post.title} ({'Acesso' if self.has_access else 'Sem acesso'})"


class MediaAccessRequest(models.Model):
    """Model to handle access requests for paid media posts"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    media_post = models.ForeignKey(MediaPost, on_delete=models.CASCADE)
    payment_slip = models.FileField(upload_to='media_access_slips/', verbose_name="Comprovante de Pagamento")
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False, verbose_name="Aprovado")

    class Meta:
        verbose_name = 'Pedido de Acesso a Mídia'
        verbose_name_plural = 'Pedidos de Acesso a Mídias'
        unique_together = ('user', 'media_post')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # If approved, grant access
        if self.approved:
            MediaAccess.objects.update_or_create(
                user=self.user,
                media_post=self.media_post,
                defaults={'has_access': True}
            )

    def __str__(self):
        return f"{self.user.fullname} - {self.media_post.title} ({'Aprovado' if self.approved else 'Pendente'})"


class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    titulo = models.CharField(max_length=200, verbose_name="Título do Produto")
    descricao = models.TextField(verbose_name="Descrição")
    area_pesquisa = models.CharField(
        max_length=50, 
        choices=RESEARCH_AREA_CHOICES, 
        verbose_name="Área de Pesquisa"
    )
    link = models.URLField(verbose_name="Link do Produto")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def __str__(self):
        return f"{self.titulo} ({self.user.fullname})"

    def get_area_pesquisa_display(self):
        return dict(RESEARCH_AREA_CHOICES).get(self.area_pesquisa, 'Desconhecida')

