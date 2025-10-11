

from django.contrib import admin
from .article_access_models import ArticleAccess, ArticleAccessRequest
from .community_message_models import CommunityMessage
from .models import MediaPost, MediaLike, MediaComment, MediaFile, MediaAccess, MediaAccessRequest, Product

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


@admin.register(MediaPost)
class MediaPostAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "file_count", "is_paid", "created_at")
    search_fields = ("title", "description", "user__fullname")
    list_filter = ("user", "created_at")
    readonly_fields = ("created_at", "updated_at")
    
    def is_paid(self, obj):
        return obj.is_paid
    is_paid.boolean = True
    is_paid.short_description = "É pago?"
    
    def file_count(self, obj):
        return obj.file_count
    file_count.short_description = "Arquivos"




@admin.register(MediaLike)
class MediaLikeAdmin(admin.ModelAdmin):
    list_display = ("user", "media_post", "created_at")
    search_fields = ("user__fullname", "media_post__title")
    list_filter = ("created_at", "media_post__user")
    readonly_fields = ("created_at",)


@admin.register(MediaComment)
class MediaCommentAdmin(admin.ModelAdmin):
    list_display = ("user", "media_post", "body_preview", "created_at")
    search_fields = ("body", "user__fullname", "media_post__title")
    list_filter = ("created_at", "media_post__user")
    readonly_fields = ("created_at", "updated_at")
    
    def body_preview(self, obj):
        return obj.body[:50] + "..." if len(obj.body) > 50 else obj.body
    body_preview.short_description = "Comentário"


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ("media_post", "media_type", "get_file_size", "created_at")
    search_fields = ("media_post__title",)
    list_filter = ("media_type", "created_at")
    readonly_fields = ("created_at", "media_type")


@admin.register(MediaAccess)
class MediaAccessAdmin(admin.ModelAdmin):
    list_display = ("user", "media_post", "has_access", "created_at")
    search_fields = ("user__fullname", "media_post__title")
    list_filter = ("has_access", "created_at")
    readonly_fields = ("created_at",)


@admin.register(MediaAccessRequest)
class MediaAccessRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "media_post", "approved", "created_at")
    search_fields = ("user__fullname", "media_post__title")
    list_filter = ("approved", "created_at")
    readonly_fields = ("created_at",)
    
    def save_model(self, request, obj, form, change):
        """Auto-grant access when request is approved"""
        super().save_model(request, obj, form, change)
        # The model's save method will handle access granting


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("titulo", "user", "area_pesquisa", "created_at")
    search_fields = ("titulo", "descricao", "user__fullname")
    list_filter = ("area_pesquisa", "created_at", "user")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


# Register your models here.

