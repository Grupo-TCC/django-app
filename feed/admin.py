

from django.contrib import admin
from .article_access_models import ArticleAccess, ArticleAccessRequest
from .community_message_models import CommunityMessage

@admin.register(ArticleAccessRequest)
class ArticleAccessRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "created_at", "approved")
    search_fields = ("user__fullname", "article__title")
    list_filter = ("approved",)

@admin.register(CommunityMessage)
class CommunityMessageAdmin(admin.ModelAdmin):
    list_display = ("community", "user", "body", "created_at")
    search_fields = ("body", "user__fullname", "community__name")
    list_filter = ("community", "user")


# Register your models here.

