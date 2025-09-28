from django.contrib import admin
from .community_message_models import CommunityMessage

@admin.register(CommunityMessage)
class CommunityMessageAdmin(admin.ModelAdmin):
    list_display = ("community", "user", "body", "created_at")
    search_fields = ("body", "user__fullname", "community__name")
    list_filter = ("community", "user")


# Register your models here.

