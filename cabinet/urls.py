from django.urls import path
from . import views

app_name = "cabinet"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("bills/", views.bills_list, name="bills_list"),
    path("bills/paid/", views.bills_paid, name="bills_paid"),
    path("bills/overdue/", views.bills_overdue, name="bills_overdue"),
    path("tariffs/", views.tariffs_active, name="tariffs_active"),
    path("tariffs/archive/", views.tariffs_archive, name="tariffs_archive"),
    path("messages/", views.messages_list, name="messages_list"),
    path("service/", views.service_request, name="service_request"),
    path("profile/", views.profile, name="profile"),
]