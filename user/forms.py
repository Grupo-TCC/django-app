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


# class InnovatorVerificationForm(forms.ModelForm):
#     class Meta:
#         model = User.InnovatorVerification
#         fields = ['title', 'institution', 'document']
#         widgets = {
#             'title': forms.TextInput(attrs={'placeholder': 'Seu cargo (ex: Estudante, Professor, Pesquisador)', 'class': 'form-control'}),
#             'institution': forms.TextInput(attrs={'placeholder': 'Sua instituição (ex: Universidade de São Paulo)', 'class': 'form-control'}),
#             'document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
#         }
        
    def clean_document(self):
        document = self.cleaned_data.get('document')
        if document:
            allowed_types = [
                'application/pdf',
                'image/png',
                'image/jpeg',
            ]
            if hasattr(document, 'content_type') and document.content_type not in allowed_types:
                raise forms.ValidationError('Tipo de arquivo não suportado. Envie PDF, PNG ou JPEG.')
        return document 

