from .community_models import Community
from django import forms
from .models import Post
from .article_models import Article

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'media']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'placeholder': 'Sobre o que você quer falar?',
            'class': 'post-textarea'
        })

    def clean_media(self):
        media = self.cleaned_data.get('media')
        if media:
            allowed_types = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-powerpoint',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                'image/png',
                'image/jpeg',
            ]
            if hasattr(media, 'content_type') and media.content_type not in allowed_types:
                raise forms.ValidationError('Tipo de arquivo não suportado. Envie PDF, DOC, DOCX, PPT, PPTX, PNG ou JPEG.')
        return media

class ArticleForm(forms.ModelForm):
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Descreva brevemente o artigo',
            'class': 'form-control',
            'rows': 4,
        }),
        label='Descrição',
    )
    ACCESS_CHOICES = [
        ('free', 'Gratuito'),
        ('paid', 'Pago'),
    ]
    access_type = forms.ChoiceField(
        choices=ACCESS_CHOICES,
        widget=forms.RadioSelect,
        label='Tipo de acesso',
        initial='free',
    )
    price = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=8,
        decimal_places=2,
        widget=forms.TextInput(attrs={'placeholder': 'Valor (R$)', 'class': 'form-control', 'style': 'width:100px;'}),
        label='Valor',
    )

    class Meta:
        model = Article
        fields = ['pdf', 'title', 'research_area', 'description', 'access_type', 'price']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Título do artigo', 'class': 'form-control'}),
            'research_area': forms.TextInput(attrs={'placeholder': 'Área de pesquisa', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        access_type = cleaned_data.get('access_type')
        price = cleaned_data.get('price')
        if access_type == 'paid' and not price:
            self.add_error('price', 'Informe o valor para artigos pagos.')
        if access_type == 'free':
            cleaned_data['price'] = None
        return cleaned_data

    def clean_pdf(self):
        pdf = self.cleaned_data.get('pdf')
        if pdf:
            if not pdf.name.lower().endswith('.pdf'):
                raise forms.ValidationError('Apenas arquivos PDF são permitidos.')
        return pdf
    

class CommunityForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['community_pic'].required = False
    class Meta:
        model = Community
        fields = ["name", "description", "community_pic"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Nome da comunidade", "class": "form-control"}),
            "description": forms.Textarea(attrs={"placeholder": "Descrição (opcional)", "class": "form-control", "rows": 3}),
            "community_pic": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

