from django.db import models
from django.conf import settings
from .constants import RESEARCH_AREA_CHOICES

class Article(models.Model):
    
    QUALIS_CAPES_CHOICES = [
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('B1', 'B1'),
        ('B2', 'B2'),
        ('B3', 'B3'),
        ('B4', 'B4'),
        ('B5', 'B5'),
        ('C', 'C'),
    ]
    
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    pdf = models.FileField(upload_to='articles/', blank=False, null=False)
    research_area = models.CharField(max_length=50, choices=RESEARCH_AREA_CHOICES)
    qualis_capes = models.CharField(max_length=2, choices=QUALIS_CAPES_CHOICES, verbose_name="Qualis Capes", default='A1')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.fullname})"
    
    def get_research_area_display(self):
        return dict(RESEARCH_AREA_CHOICES).get(self.research_area, 'Desconhecida')
