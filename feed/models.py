
from django.db import models
from django.conf import settings
from django.utils import timezone

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

class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']  # oldest → newest (change if you want)

    def __str__(self):
        return f"{self.user.email}: {self.body[:30]}"