from django.urls import path
from . import views
from .views import (
    PaymentItemListView,
    PaymentItemCreateView,
    HouseListView,
    HouseCreateView,
    HouseDetailView,
    HouseDeleteView,
    HouseUpdateView,
)

app_name = "adminpanel"

urlpatterns = [
    path("admin/house/index", HouseListView.as_view(), name="house_index"),
    path("admin/house/create", HouseCreateView.as_view(), name="house_create"),
    path("admin/house/<int:pk>", HouseDetailView.as_view(), name="house_detail"),
    path("admin/house/<int:pk>/edit", HouseUpdateView.as_view(), name="house_edit"),
    path("admin/house/<int:pk>/delete", HouseDeleteView.as_view(), name="house_delete"),
    path(
        "transaction-purpose/<int:pk>/edit",
        views.PaymentItemUpdateView.as_view(),
        name="payment_items_edit",
    ),
    path(
        "transaction-purpose/<int:pk>/delete",
        views.PaymentItemDeleteView.as_view(),
        name="payment_items_delete",
    ),
    path(
        "transaction-purpose/index",
        PaymentItemListView.as_view(),
        name="payment_items_list",
    ),
    path(
        "transaction-purpose/create",
        PaymentItemCreateView.as_view(),
        name="payment_items_create",
    ),
    path(
        "users/", views.UsersPageView.as_view(), name="user_list"
    ),  # страница со столом
    path("users/<int:pk>/edit/", views.UserUpdateView.as_view(), name="user_edit"),
    path("users/<int:pk>/delete/", views.UserDeleteView.as_view(), name="user_delete"),
    path("users/create/", views.UserCreateView.as_view(), name="user_add"),
    path("users/<int:pk>/", views.UserDetailView.as_view(), name="user_detail"),
    path("roles/", views.RoleMatrixView.as_view(), name="role_matrix"),
    path("roles/<int:pk>/", views.RoleEditView.as_view(), name="role_edit"),
    path("requisites/", views.PaymentDetailsUpdateView.as_view(), name="requisites"),
    path("", views.dashboard, name="dashboard"),
    path("cashdesk/", views.cashdesk, name="cashdesk"),
    path("receipts/", views.pay_receipts, name="pay_receipts"),
    path("accounts/", views.accounts, name="accounts"),
    path("apartments/", views.apartments, name="apartments"),
    path("owners/", views.owners, name="owners"),
    path("houses/", views.houses, name="houses"),
    path("messages/", views.messages1, name="messages"),
    path("requests/", views.requests, name="requests"),
    path("meters/", views.meters, name="meters"),
    path("site/", views.site, name="site"),
    path("settings/", views.settings, name="settings"),
    path("profile/", views.profile, name="profile"),
]
