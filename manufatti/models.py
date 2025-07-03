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

class info_idriche(models.Model):
    manufatto = models.ForeignKey('Manufatto', on_delete=models.CASCADE, related_name='info_idriche')
    portata = models.FloatField(null=True, blank=True)
    pressione = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Info idriche di {self.manufatto.nome}"


class info_geografiche(models.Model):
    manufatto = models.ForeignKey('Manufatto', on_delete=models.CASCADE, related_name='info_geografiche')
    latitudine = models.FloatField(null=True, blank=True)
    longitudine = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"info geografiche {self.manufatto.nome}"