from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import ManufattoForm, InfoIdricheForm, InfoGeograficheForm

@login_required
def crea_manufatto(request):
    if request.method == 'POST':
        form_manufatto = ManufattoForm(request.POST)
        form_idriche = InfoIdricheForm(request.POST)
        form_geografiche = InfoGeograficheForm(request.POST)

        if form_manufatto.is_valid() and form_idriche.is_valid() and form_geografiche.is_valid():
            manufatto = form_manufatto.save()

            idriche = form_idriche.save(commit=False)
            idriche.manufatto = manufatto
            idriche.save()

            geo = form_geografiche.save(commit=False)
            geo.manufatto = manufatto
            geo.save()

            return redirect('lista_manufatti')  # oppure altra view
    else:
        form_manufatto = ManufattoForm()
        form_idriche = InfoIdricheForm()
        form_geografiche = InfoGeograficheForm()

    return render(request, 'manufatti/crea_manufatto.html', {
        'form_manufatto': form_manufatto,
        'form_idriche': form_idriche,
        'form_geografiche': form_geografiche,
    })

from .models import Manufatto

@login_required
def lista_manufatti(request):
    manufatti = Manufatto.objects.all()
    return render(request, 'manufatti/lista_manufatti.html', {'manufatti': manufatti})