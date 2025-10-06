from django import forms
from .models import Manufatto, info_idriche, info_geografiche, Documento


class ManufattoForm(forms.ModelForm):
    class Meta:
        model = Manufatto
        fields = ['nome', 'stato']  # Solo i campi presenti nel modello
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Inserisci il nome'}),
            'stato': forms.Select(attrs={'class': 'form-select'}),
        }


class InfoIdricheForm(forms.ModelForm):
    class Meta:
        model = info_idriche
        fields = ['portata', 'pressione']
        widgets = {
            'portata': forms.NumberInput(attrs={'class': 'form-control'}),
            'pressione': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class InfoGeograficheForm(forms.ModelForm):
    class Meta:
        model = info_geografiche
        fields = ['latitudine', 'longitudine']
        widgets = {
            'latitudine': forms.NumberInput(attrs={'class': 'form-control'}),
            'longitudine': forms.NumberInput(attrs={'class': 'form-control'}),
        }
class DocumentoForm(forms.ModelForm):
    # NUOVO METODO AGGIUNTO
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['manufatto'].empty_label = "Nessun manufatto (documento generale)"
        self.fields['manufatto'].label = "Associa a un manufatto (opzionale)"

    class Meta:
        model = Documento
        fields = ['manufatto', 'titolo', 'file']
        widgets = {
            'manufatto': forms.Select(attrs={'class': 'form-select'}),
            'titolo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titolo del documento'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }