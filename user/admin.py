from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str    
from django.contrib.auth.tokens import default_token_generator 
from django.conf import settings
from .models import UserVerification
from feed.community_models import Community
from feed.models import Post



# -------- User admin --------
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ('email', 'fullname', "email_verified", 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active', "email_verified" )

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('fullname', "profile_picture" )}),
        ("Verification", {"fields": ("email_verified",)}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'fullname', 'password1', 'password2', "profile_picture"),
        }),
    )

    ordering = ('email',)
    search_fields = ('email', 'fullname')


@admin.register(UserVerification)
class UserVerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "link", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__email", "link")

    actions = ["approve_users", "reject_users"]

    def approve_users(self, request, queryset):
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.contrib.auth.tokens import default_token_generator
        for verification in queryset:
            user = verification.user
            verification.status = "APPROVED"
            verification.save()
            # Generate uidb64 and token for the user
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            # Build login URL matching the auto_login view
            login_url = request.build_absolute_uri(
                reverse("user:auto_login", args=[uidb64, token])
            )
            send_mail(
                "Sua conta foi aprovada!",
                f"Parabéns, {user.fullname}! Você pode acessar sua conta por este link:\n\n{login_url}",
                settings.EMAIL_HOST_USER,
                [user.email],
            )
        self.message_user(request, "Usuários aprovados e link enviado.")

    def reject_users(self, request, queryset):
        for verification in queryset:
            verification.status = "REJECTED"
            verification.save()
            send_mail(
                "Sua verificação foi rejeitada",
                "Infelizmente seu cadastro não foi aprovado. Revise o link enviado ou contate o suporte.",
                settings.EMAIL_HOST_USER,
                [verification.user.email],
            )
        self.message_user(request, "Usuários rejeitados e aviso enviado.")


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "created_at")

admin.site.register(Post)


