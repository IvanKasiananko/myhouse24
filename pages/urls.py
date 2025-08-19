from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.index, name='home'),      # Главная
    path('about/', views.about, name='about'),# О нас
    path('services/', views.services, name='services'), # Услуги
    path('terms/', views.terms, name='terms'), # Условия приобретения
    path('contacts/', views.contacts, name='contacts'), # Контакты
]
