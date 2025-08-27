from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from .models import User, ResearchArea, InnovatorVerification
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.utils.html import format_html
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode




# -------- User admin --------
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ('email', 'fullname', 'is_staff', 'is_superuser', 'user_type')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'user_type')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('fullname', 'user_type')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'fullname', 'user_type', 'password1', 'password2'),
        }),
    )

    ordering = ('email',)
    search_fields = ('email', 'fullname')


admin.site.register(User, CustomUserAdmin)

# -------- ResearchArea admin --------
@admin.register(ResearchArea)
class ResearchAreaAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    ordering = ('name',)

# -------- InnovatorVerification admin --------
@admin.register(InnovatorVerification)
class InnovatorVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'applicant_type', 'status', 'created_at', 'document_link')
    list_filter = ('status', 'applicant_type')
    search_fields = ('user__email', 'user__fullname')
    
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': (
                'user',
                'applicant_type',
                
                'title',
                'document',
                'status',
                'created_at',
            )
        }),
    )

    actions = ('approve_and_activate', 'reject')

    def document_link(self, obj):
        if obj.document:
            return format_html('<a href="{}" target="_blank">Abrir documento</a>', obj.document.url)
        return '-'
    document_link.short_description = 'Documento'

    def approve_and_activate(self, request, queryset):
        """Mark verification as APPROVED and activate the user account."""
        updated = 0
        for obj in queryset.select_related('user'):
            user = obj.user
            
            # Set status to approved
            if obj.status != 'APPROVED':
                obj.status = 'APPROVED'
                obj.save(update_fields=['status'])
            
            # Activate user ONLY if email verified already
            if obj.user.email_verified and not obj.user.is_active:
                obj.user.is_active = True
                user.save(update_fields=['is_active'])
            
            # Always send a login link if the account is active    
            try:
                if user.is_active:
                    uidb64 = urlsafe_base64_encode(str(user.pk).encode())
                    token = default_token_generator.make_token(user)
                    login_path = reverse('user:auto_login', args=[uidb64, token])
                    login_url = request.build_absolute_uri(login_path)
                    
                    send_mail(
                        subject="Sua conta de Inovador foi aprovada",
                        message=(
                            "Parabéns! Sua conta de Inovador foi aprovada.\n\n"
                            "Clique no link abaixo para acessar diretamente sua conta:\n"
                            f"{login_url}\n\n"
                            "Se você não solicitou, ignore este email."
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[obj.user.email],
                        fail_silently=True,
                    )
            except Exception:
                pass
            updated += 1
        self.message_user(request, f"{updated} solicitação(ões) aprovada(s) e usuários ativados.")
    approve_and_activate.short_description = "Aprovar, ativar (se verificado) e enviar link de login"

    def reject(self, request, queryset):
        count = 0
        for obj in queryset.select_related('user'):
            obj.status = 'REJECTED'
            obj.save(update_fields=['status'])
            # Notify
            try:
                send_mail(
                    subject="Sua solicitação de Inovador foi rejeitada",
                    message=(
                        "Sua solicitação não pôde ser aprovada no momento. "
                        "Verifique seus documentos e tente novamente."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[obj.user.email],
                    fail_silently=True,
                )
            except Exception:
                pass
            count += 1
        self.message_user(request, f"{count} solicitação(ões) rejeitada(s).")
    reject.short_description = "Rejeitar e notificar por email"
