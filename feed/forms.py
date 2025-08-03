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
        
