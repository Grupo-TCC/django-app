from .community_models import Community
from django import forms
from .models import MediaPost, Product
from django.forms.widgets import FileInput
from .constants import RESEARCH_AREA_CHOICES

from .article_models import Article




class ArticleForm(forms.ModelForm):
    # Use existing choices that already include 'outro' option
    
    research_area_select = forms.ChoiceField(
        choices=RESEARCH_AREA_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-control", "id": "research_area_select"}),
        label="Área de Pesquisa"
    )
    
    research_area_custom = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Digite sua área de pesquisa", 
            "class": "form-control",
            "id": "research_area_custom",
            "style": "display: none;"
        }),
        label="Área de Pesquisa Personalizada"
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Descreva brevemente o artigo',
            'class': 'form-control',
            'rows': 4,
        }),
        label='Resumo',
    )

    class Meta:
        model = Article
        fields = ['pdf', 'title', 'research_area', 'qualis_capes', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Título do artigo', 'class': 'form-control'}),
            'research_area': forms.HiddenInput(),  # Hidden field that will store the final value
            'qualis_capes': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values for the custom fields based on existing research_area
        if self.instance and self.instance.research_area:
            # Check if the research area matches one of our predefined choices
            for choice_key, choice_label in RESEARCH_AREA_CHOICES:
                if choice_key == self.instance.research_area or choice_label == self.instance.research_area:
                    self.fields['research_area_select'].initial = choice_key
                    break
            else:
                # If not found in predefined choices, set as outro and use custom field
                self.fields['research_area_select'].initial = 'outro'
                self.fields['research_area_custom'].initial = self.instance.research_area

    def clean_pdf(self):
        pdf = self.cleaned_data.get('pdf')
        if pdf:
            if not pdf.name.lower().endswith('.pdf'):
                raise forms.ValidationError('Apenas arquivos PDF são permitidos.')
        return pdf
    
    def clean(self):
        cleaned_data = super().clean()
        research_area_select = cleaned_data.get('research_area_select')
        research_area_custom = cleaned_data.get('research_area_custom')
        
        if research_area_select == 'outro':
            if not research_area_custom or not research_area_custom.strip():
                raise forms.ValidationError('Por favor, especifique sua área de pesquisa.')
            self.cleaned_data['research_area'] = research_area_custom.strip()
        elif research_area_select:
            # Use the choice key directly for predefined options
            self.cleaned_data['research_area'] = research_area_select
        
        return self.cleaned_data

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


class MediaPostForm(forms.ModelForm):
    PAYMENT_CHOICES = [
        ('free', 'Grátis'),
        ('paid', 'Pago'),
    ]
    
    # Use existing choices that already include 'outro' option
    
    research_area_select = forms.ChoiceField(
        choices=RESEARCH_AREA_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-control", "id": "research_area_select_media"}),
        label="Área de Pesquisa"
    )
    
    research_area_custom = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Digite sua área de pesquisa", 
            "class": "form-control",
            "id": "research_area_custom_media",
            "style": "display: none;"
        }),
        label="Área de Pesquisa Personalizada"
    )
    
    payment_type = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        label='Tipo de acesso',
        initial='free',
    )
    
    price = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=8,
        decimal_places=2,
        widget=forms.TextInput(attrs={
            'placeholder': 'Valor (R$)', 
            'class': 'form-control', 
            'style': 'width:150px;'
        }),
        label='Preço (R$)',
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Set initial values for the custom fields based on existing research_area
        if self.instance and self.instance.research_area:
            # Check if the research area matches one of our predefined choices
            for choice_key, choice_label in RESEARCH_AREA_CHOICES:
                if choice_key == self.instance.research_area or choice_label == self.instance.research_area:
                    self.fields['research_area_select'].initial = choice_key
                    break
            else:
                # If not found in predefined choices, set as outro and use custom field
                self.fields['research_area_select'].initial = 'outro'
                self.fields['research_area_custom'].initial = self.instance.research_area
    
    # This field won't be rendered - we use JavaScript to create the actual file inputs
    # But we need it for form validation
    media_files = forms.Field(required=False)
        
    class Meta:
        model = MediaPost
        fields = ["title", "description", "research_area", "payment_type", "price"]
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Título", 
                "class": "form-control",
                "maxlength": "200"
            }),
            "description": forms.Textarea(attrs={
                "placeholder": "Descreva sua publicação", 
                "class": "form-control", 
                "rows": 4
            }),
            "research_area": forms.HiddenInput(),  # Hidden field that will store the final value
        }
        
    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get('payment_type')
        price = cleaned_data.get('price')
        
        if payment_type == 'paid' and not price:
            self.add_error('price', 'Informe o valor para conteúdo pago.')
        
        # Validate uploaded files
        files = self.files.getlist('media_files')
        
        if not files:
            raise forms.ValidationError("Selecione pelo menos um arquivo.")
        
        if len(files) > 10:  # Limit to 10 files per post
            raise forms.ValidationError("Máximo de 10 arquivos por post.")
        
        total_size = 0
        for file in files:
            # Check individual file size (50MB limit)
            if file.size > 50 * 1024 * 1024:
                raise forms.ValidationError(f"O arquivo '{file.name}' é muito grande. O tamanho máximo é de 50MB por arquivo.")
            
            total_size += file.size
            
            # Check file type
            allowed_types = [
                # Images
                'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp',
                # Videos
                'video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/quicktime', 'video/webm',
                # Documents
                'application/pdf',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # .pptx
                'application/vnd.ms-powerpoint',  # .ppt
            ]
            
            # Also check by file extension as a fallback
            import os
            file_extension = os.path.splitext(file.name)[1].lower()
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', 
                                '.mp4', '.avi', '.mov', '.wmv', '.webm', '.mkv',
                                '.pdf', '.pptx', '.ppt']
            
            if file.content_type not in allowed_types and file_extension not in allowed_extensions:
                raise forms.ValidationError(
                    f"Arquivo '{file.name}' não é suportado. Use formatos de imagem (JPG, PNG, GIF, etc.), vídeo (MP4, AVI, MOV, etc.) ou documentos (PDF, PPTX)."
                )
        
        # Check total size (200MB limit for all files combined)
        if total_size > 200 * 1024 * 1024:
            raise forms.ValidationError("O tamanho total dos arquivos não pode exceder 200MB.")
        
        # Handle custom research area
        research_area_select = cleaned_data.get('research_area_select')
        research_area_custom = cleaned_data.get('research_area_custom')
        
        if research_area_select == 'outro':
            if not research_area_custom or not research_area_custom.strip():
                raise forms.ValidationError('Por favor, especifique sua área de pesquisa.')
            self.cleaned_data['research_area'] = research_area_custom.strip()
        elif research_area_select:
            # Use the choice key directly for predefined options
            self.cleaned_data['research_area'] = research_area_select
            
        return self.cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set the user if provided
        if self.user:
            instance.user = self.user
        
        # Get uploaded files
        files = self.files.getlist('media_files')
        

        
        if commit:
            instance.save()
            
            # Create MediaFile objects for all uploaded files
            from .models import MediaFile
            for file in files:
                MediaFile.objects.create(
                    media_post=instance,
                    media_file=file
                )
            
        return instance


class ProductForm(forms.ModelForm):
    # Use existing choices that already include 'outro' option
    
    research_area_select = forms.ChoiceField(
        choices=RESEARCH_AREA_CHOICES,
        required=True,
        widget=forms.Select(attrs={"class": "form-control", "id": "research_area_select_product"}),
        label="Área de Pesquisa"
    )
    
    research_area_custom = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Digite sua área de pesquisa", 
            "class": "form-control",
            "id": "research_area_custom_product",
            "style": "display: none;"
        }),
        label="Área de Pesquisa Personalizada"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values for the custom fields based on existing area_pesquisa
        if self.instance and self.instance.area_pesquisa:
            # Check if the area_pesquisa matches one of our predefined choices
            for choice_key, choice_label in RESEARCH_AREA_CHOICES:
                if choice_key == self.instance.area_pesquisa or choice_label == self.instance.area_pesquisa:
                    self.fields['research_area_select'].initial = choice_key
                    break
            else:
                # If not found in predefined choices, set as outro and use custom field
                self.fields['research_area_select'].initial = 'outro'
                self.fields['research_area_custom'].initial = self.instance.area_pesquisa

    def clean(self):
        cleaned_data = super().clean()
        research_area_select = cleaned_data.get('research_area_select')
        research_area_custom = cleaned_data.get('research_area_custom')
        
        if research_area_select == 'outro':
            if not research_area_custom or not research_area_custom.strip():
                raise forms.ValidationError('Por favor, especifique sua área de pesquisa.')
            cleaned_data['area_pesquisa'] = research_area_custom.strip()
        elif research_area_select:
            # Find the display name for the selected choice
            for choice_key, choice_label in RESEARCH_AREA_CHOICES:
                if choice_key == research_area_select:
                    cleaned_data['area_pesquisa'] = choice_key
                    break
        
        return cleaned_data
    
    class Meta:
        model = Product
        fields = ['titulo', 'descricao', 'area_pesquisa', 'link']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'placeholder': 'Título do produto',
                'class': 'form-control'
            }),
            'descricao': forms.Textarea(attrs={
                'placeholder': 'Descreva seu produto (app, projeto, ferramenta, etc.)',
                'class': 'form-control',
                'rows': 4,
            }),
            'area_pesquisa': forms.HiddenInput(),  # Hide the actual model field
            'link': forms.URLInput(attrs={
                'placeholder': 'https://exemplo.com/seu-produto',
                'class': 'form-control'
            }),
        }
        labels = {
            'titulo': 'Título do Produto',
            'descricao': 'Descrição',
            'area_pesquisa': 'Área de Pesquisa',
            'link': 'Link do Produto',
        }

