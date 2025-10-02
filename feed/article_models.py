from django.db import models
from django.conf import settings

class Article(models.Model):
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    pdf = models.FileField(upload_to='articles/', blank=False, null=False)
    research_area = models.CharField(max_length=100)
    access_type = models.CharField(max_length=10, choices=[('free', 'Gratuito'), ('paid', 'Pago')], default='free')
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.fullname})"
