from django import forms
from django.contrib.auth.models import User

ENTI = [
    ('AATO', 'AATO'),
    ('TEA', 'TEA'),
]

class UserProfiloForm(forms.Form):
    first_name = forms.CharField(label='Nome', max_length=100)
    last_name = forms.CharField(label='Cognome', max_length=100)
    username = forms.CharField(label="Username", max_length=150)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    ente = forms.ChoiceField(label="Ente", choices=ENTI)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Questo username è già in uso.")
        return username
