from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import UserProfiloForm
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404

from .models import Profilo


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            ente = user.profilo.ente
            if ente == 'ADMIN':
                return redirect('admin_dashboard')
            if ente == 'AATO':
                return redirect('aato')
            elif ente == 'TEA':
                return redirect('tea')
        else:
            messages.error(request, 'Credenziali non valide.')
    return render(request, 'accounts/login.html')

def tea_view(request):
    return render(request, 'accounts/tea_home.html')

def aato_view(request):
    return render(request, 'accounts/aato_home.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def registra_utente(request):
    if request.method == 'POST':
        form = UserProfiloForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            Profilo.objects.create(
                user=user,
                ente=form.cleaned_data['ente']
            )
            return redirect('login')
    else:
        form = UserProfiloForm()
    return render(request, 'accounts/registrazione.html', {'form': form})

@login_required
def admin_dashboard(request):
    # Solo chi ha l'ente ADMIN può accedere
    if request.user.profilo.ente != 'ADMIN':
        return redirect('login')
    
    utenti = User.objects.all().select_related('profilo')
    return render(request, 'accounts/admin_dashboard.html', {'utenti': utenti})

@login_required
def elimina_utente(request, user_id):
    if request.user.profilo.ente == 'ADMIN':
        utente_da_eliminare = get_object_or_404(User, id=user_id)
        utente_da_eliminare.delete() # Elimina User e Profilo associato
    return redirect('admin_dashboard')
