
from django import forms
from .models import Interface

class InterfaceForm(forms.ModelForm):
    template_name = "normal/form.html"
    
    class Meta:
        model = Interface
        fields = "__all__"