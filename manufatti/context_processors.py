from accounts.models import Profilo

from accounts.models import Profilo

# Cambia il nome qui per farlo coincidere con settings.py
def ente_utente_context(request): 
    if request.user.is_authenticated:
        try:
            profilo = Profilo.objects.get(user=request.user)
            return {'ente_utente': profilo.ente}
        except Exception:
            return {'ente_utente': 'TEA'}
    return {'ente_utente': None}