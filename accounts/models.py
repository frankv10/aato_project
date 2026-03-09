from django.db import models
from django.contrib.auth.models import User

ENTI = [
    ('AATO', 'AATO'),
    ('TEA', 'AqA'),
    ('ADMIN', 'Amministratore di Sistema'),
]

class Profilo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ente = models.CharField(max_length=10, choices=ENTI)

    def __str__(self):
        return f"{self.user.username} - {self.ente}"


