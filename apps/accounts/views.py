from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import User

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)

        if user is None:
            messages.error(request, "Email ou senha inválidos.")
            return redirect("accounts:login")

        login(request, user)
        return redirect("landing:index") # tenho que mudar esse caminho tbm
    return render(request, "accounts/pages/login.html")

def cadastro_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            messages.error(request, "As senhas não coincidem.")
            return redirect("accounts:cadastro")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Este email já está cadastrado.")
            return redirect("accounts:cadastro")

        user = User.objects.create_user(
            email=email,
            password=password
        )
        
        login(request, user)
        messages.success(request, "Conta criada com sucesso!")
        return redirect("landing:index") # tenho que mudar isso depois
    return render(request, "accounts/pages/cadastro.html")