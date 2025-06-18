from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Manufatto

@login_required
def crea_manufatto(request):
    if request.method == 'POST':
        nome= request.POST.get('nome')
        stato = request.POST.get('stato')
        Manufatto.objects.create(nome=nome, stato=stato)
    return render(request, 'manufatti/crea_manufatto.html')