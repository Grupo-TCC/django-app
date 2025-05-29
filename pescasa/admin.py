from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ResearchArea
from .forms import CustomUserCreationForm, CustomUserChangeForm




class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ('email', 'fullname', 'is_staff', 'is_superuser', 'user_type')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'user_type')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('fullname', 'research_areas', 'user_type')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'fullname', 'research_areas', 'user_type', 'password1', 'password2'),
        }),
    )

    ordering = ('email',)
    search_fields = ('email', 'fullname')


admin.site.register(User, CustomUserAdmin)
