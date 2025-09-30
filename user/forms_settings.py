from django import forms
from .models import User

class UserResearchInstitutionForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["research_area", "institution"]
        widgets = {
            "research_area": forms.TextInput(attrs={"placeholder": "Área de Pesquisa"}),
            "institution": forms.TextInput(attrs={"placeholder": "Instituição"}),
        }
