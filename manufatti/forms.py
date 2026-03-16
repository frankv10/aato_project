import os
from django import forms
from django.core.management.base import BaseCommand
from manufatti.models import Manufatto, info_idriche, info_geografiche, Documento


class ManufattoForm(forms.ModelForm):
    class Meta:
        model = Manufatto
        # Campi base del manufatto
        fields = ['nome', 'stato', 'comune', 'localita', 'ubicazione', 'depuratore_associato', 'recapito_emissario', 'tipologia_sfioratore']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Codice Manufatto (es. SF-BGN-ALL1)'}),
            'stato': forms.Select(attrs={'class': 'form-select'}),
            'comune': forms.TextInput(attrs={'class': 'form-control'}),
            'localita': forms.TextInput(attrs={'class': 'form-control'}),
            'ubicazione': forms.TextInput(attrs={'class': 'form-control'}),
            'depuratore_associato': forms.TextInput(attrs={'class': 'form-control'}),
            'recapito_emissario': forms.TextInput(attrs={'class': 'form-control'}),
            'tipologia_sfioratore': forms.TextInput(attrs={'class': 'form-control'}),
        }


class InfoIdricheForm(forms.ModelForm):
    class Meta:
        model = info_idriche
        # Rimuove 'manufatto' (gestito dalla vista) e include tutti i campi idrici
        exclude = ['manufatto']
        # Applica lo stile form-control a tutti i widget
        widgets = {
            field_name: forms.TextInput(attrs={'class': 'form-control'}) 
            for field_name in info_idriche._meta.get_fields() if field_name.name != 'manufatto' and field_name.name != 'id'
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['manufatto'].empty_label = "Nessun manufatto (documento generale)"
        self.fields['manufatto'].label = "Associa a un manufatto (opzionale)"
        # Forza l'attributo multiple qui per evitare il ValueError di sistema
        self.fields['file'].widget.attrs.update({'multiple': True})

    class Meta:
        model = Documento
        fields = ['manufatto', 'titolo', 'file']
        widgets = {
            'manufatto': forms.Select(attrs={'class': 'form-select'}),
            'titolo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titolo del documento'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}), # Rimosso 'multiple' da qui
        }