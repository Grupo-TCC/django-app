from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


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
    title = forms.CharField(
        label='',
        required=False,  # change to True if mandatory
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Curso (ex: Ciência da Computação)'})
    )

    
    
    
    class Meta:
        model = User  # Your CustomUser model
        fields = ('email', 'fullname')
        
    
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
        fields = ('email', 'fullname', 'is_active', 'is_staff')
        

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["profile_picture"]

