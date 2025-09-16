from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm



# -------- User admin --------
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


admin.site.register(User, CustomUserAdmin)
