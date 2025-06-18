from django.db import models


class Manufatto(models.Model):
    nome = models.CharField(max_length=100)
    stato = models.CharField(max_length=50, choices=[
        ('PROGRAMMATO', 'PROGRAMMATO'),
        ('IN CORSO', 'IN CORSO',),
        ('COMPLETATO', 'COMPLETATO')
    ])
    data_creazione = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome