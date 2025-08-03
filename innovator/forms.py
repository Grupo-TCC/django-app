from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, USER_TYPE


class LoginForms(forms.Form):
    email = forms.EmailField(
        label='',
        required=True,
        max_length=100,
        widget=forms.EmailInput(attrs={'placeholder': 'Email' })
        
    )
    
    
    password = forms.CharField(
        label='',
        required=True,
        max_length=70,
        widget=forms.PasswordInput(attrs={'placeholder': 'Senha'})
    )
    
class CustomUserCreationForm(UserCreationForm):
    
        
    fullname = forms.CharField(
        label='',
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Nome completo'})
    )
    email = forms.EmailField(
        label='',
        required=True,
        max_length=100,
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )
    
    # research_areas = forms.ModelMultipleChoiceField(
    #     queryset= ResearchArea.objects.none(),
    #     required=True,
    #     widget=forms.CheckboxSelectMultiple
    # )
    
    user_type = forms.ChoiceField(
        label='',
        choices=USER_TYPE,
        widget=forms.Select,
        required=True
    )
    
    class Meta:
        model = User  # Your CustomUser model
        fields = ('email', 'fullname', 'user_type')
        
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize password field labels/placeholders
        # self.fields['research_areas'].queryset = ResearchArea.objects.all()
        self.fields['password1'].widget.attrs.update({'placeholder': 'Senha'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirma Senha'})
        self.fields['password1'].label = ''
        self.fields['password2'].label = ''
        
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'fullname', 'user_type', 'is_active', 'is_staff')