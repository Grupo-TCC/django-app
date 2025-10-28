from django import forms
from .models import User
from feed.constants import RESEARCH_AREA_CHOICES

class UserResearchInstitutionForm(forms.ModelForm):
    # Use existing choices that already include 'outro' option
    
    research_area_select = forms.ChoiceField(
        choices=RESEARCH_AREA_CHOICES,
        required=False,
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
    
    class Meta:
        model = User
        fields = ["research_area", "institution", "estado", "cidade"]
        widgets = {
            "research_area": forms.HiddenInput(),  # Hidden field that will store the final value
            "institution": forms.TextInput(attrs={"placeholder": "Instituição", "class": "form-control"}),
            "estado": forms.TextInput(attrs={"placeholder": "Estado", "class": "form-control"}),
            "cidade": forms.TextInput(attrs={"placeholder": "Cidade", "class": "form-control"}),
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
    
    def clean(self):
        cleaned_data = super().clean()
        research_area_select = cleaned_data.get('research_area_select')
        research_area_custom = cleaned_data.get('research_area_custom')
        
        if research_area_select == 'outro':
            if not research_area_custom:
                raise forms.ValidationError("Por favor, especifique sua área de pesquisa.")
            cleaned_data['research_area'] = research_area_custom
        elif research_area_select:
            # Get the display name for the selected choice
            for choice_key, choice_label in RESEARCH_AREA_CHOICES:
                if choice_key == research_area_select:
                    cleaned_data['research_area'] = choice_label
                    break
        
        return cleaned_data
