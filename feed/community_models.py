from django.db import models
from django.conf import settings

class Community(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_communities")
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="joined_communities", blank=True)
    community_pic = models.ImageField(upload_to='community_pics/', blank=True, null=True)

    def __str__(self):
        return self.name

    def get_community_picture_url(self):
        if self.community_pic:
            return self.community_pic.url
        return settings.STATIC_URL + "assets/img/no_pic.jpg"
