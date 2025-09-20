from django import forms
from .models import Post

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

