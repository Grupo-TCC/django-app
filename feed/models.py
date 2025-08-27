from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    media = models.FileField(upload_to='uploads/', blank=True, null=True)
    
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_posts',
        blank=True
    )
    
    def like_count(self):
        return self.likes.count()

    def __str__(self):
        return f"{self.user.fullname}: {self.content[:30]}"

