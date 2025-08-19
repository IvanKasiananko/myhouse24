from django.shortcuts import render


def index(request):
    return render(request, 'pages/index.html')


def about(request):
    return render(request, 'pages/about.html')


def services(request):
    return render(request, 'pages/services.html')


def terms(request):
    return render(request, 'pages/terms.html')


def contacts(request):
    return render(request, 'pages/contacts.html')


from django.shortcuts import render

# Create your views here.
