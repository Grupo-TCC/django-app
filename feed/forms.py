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
    class Meta:
        model = Article
        fields = ['pdf', 'title', 'research_area']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Título do artigo', 'class': 'form-control'}),
            'research_area': forms.TextInput(attrs={'placeholder': 'Área de pesquisa', 'class': 'form-control'}),
        }

    def clean_pdf(self):
        pdf = self.cleaned_data.get('pdf')
        if pdf:
            if not pdf.name.lower().endswith('.pdf'):
                raise forms.ValidationError('Apenas arquivos PDF são permitidos.')
        return pdf

