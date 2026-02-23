from django.shortcuts import render

def index(request):
    return render(request, 'landing/pages/index.html')

def sobre(request):
    return render(request, 'landing/pages/sobre.html')

def funcionalidades(request):
    return render(request, 'landing/pages/funcionalidades.html')