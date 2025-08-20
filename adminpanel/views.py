from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, DetailView, UpdateView
from ajax_datatable.views import AjaxDatatableView
from django.db.models import Q
from django.contrib import messages

from core.models import User, Role, Permission
from .forms import UserCreateForm


class UsersPageView(TemplateView):
    """Просто отдаём шаблон со столом и фильтрами."""

    template_name = "adminpanel/users/list_ajax.html"
    login_url = reverse_lazy("login")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["roles"] = Role.objects.all().order_by("name")
        return ctx


class UsersAjaxDataView(AjaxDatatableView):
    """Серверная выдача для DataTables."""

    model = User
    title = "Users"
    initial_order = [["id", "asc"]]
    length_menu = [[10, 25, 50, 100], [10, 25, 50, 100]]
    search_values_separator = " "  # space = AND

    # колонки DataTables (имена = data в JS)
    column_defs = [
        {"name": "id", "visible": True, "searchable": False, "orderable": True},
        {"name": "full_name", "visible": True, "searchable": True, "orderable": True},
        {
            "name": "role__name",
            "title": "Роль",
            "visible": True,
            "searchable": True,
            "orderable": True,
        },
        {"name": "phone", "visible": True, "searchable": True, "orderable": False},
        {
            "name": "email",
            "title": "Email",
            "visible": True,
            "searchable": True,
            "orderable": False,
        },
        {
            "name": "is_active",
            "title": "Статус",
            "visible": True,
            "searchable": False,
            "orderable": False,
        },
        {
            "name": "actions",
            "title": "Действия",
            "searchable": False,
            "orderable": False,
            "className": "text-end",
        },
    ]

    def get_initial_queryset(self, request=None):
        return User.objects.select_related("role").all()

    # поддержка фильтров сверху (имена должны совпасть с параметрами в ajax.data)
    def filter_queryset(self, params, qs):
        q_name = params.get("q_name")
        q_phone = params.get("q_phone")
        q_email = params.get("q_email")
        q_role = params.get("q_role")
        q_status = params.get("q_status")

        if q_name:
            qs = qs.filter(
                Q(first_name__icontains=q_name)
                | Q(last_name__icontains=q_name)
                | Q(username__icontains=q_name)
            )
        if q_phone:
            qs = qs.filter(phone__icontains=q_phone)
        if q_email:
            qs = qs.filter(email__icontains=q_email)
        if q_role:
            qs = qs.filter(role_id=q_role)
        if q_status == "active":
            qs = qs.filter(is_active=True)
        elif q_status == "disabled":
            qs = qs.filter(is_active=False)
        return qs

    # как рисуем виртуальные колонки
    def prepare_results(self, qs):
        results = []
        for u in qs:
            full_name = u.get_full_name() or u.username
            status_html = (
                '<span class="badge users-badge users-badge--green">Активен</span>'
                if u.is_active
                else '<span class="badge users-badge users-badge--red">Отключен</span>'
            )
            actions_html = (
                f'<a class="act" title="Просмотр" href="{reverse_lazy("adminpanel:user_detail", args=[u.pk])}">👁</a>'
                f'<a class="act" title="Редактировать" href="#">✎</a>'
                f'<a class="act danger" title="Удалить" href="#">🗑</a>'
            )
            results.append(
                {
                    "id": u.id,
                    "full_name": f'<a class="users-name" href="{reverse_lazy("adminpanel:user_detail", args=[u.pk])}">{full_name}</a>',
                    "role__name": u.role.name if u.role_id else "—",
                    "phone": u.phone or "—",
                    "email": u.email or "—",
                    "is_active": status_html,
                    "actions": actions_html,
                }
            )
        return results


class UserDetailView(DetailView):
    model = User
    template_name = "adminpanel/users/detail.html"
    context_object_name = "user"
    login_url = reverse_lazy("login")


class UserCreateView(CreateView):
    model = User
    form_class = UserCreateForm
    template_name = "adminpanel/users/create.html"
    success_url = reverse_lazy("adminpanel:user_list")
    login_url = reverse_lazy("login")


class RoleMatrixView(TemplateView):
    template_name = "adminpanel/roles/matrix.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["roles"] = Role.objects.all().prefetch_related("permissions")
        ctx["perms"] = Permission.objects.all()
        return ctx

    def post(self, request, *args, **kwargs):
        # очищаем все связи
        for r in Role.objects.all():
            r.permissions.clear()

        # сохраняем новые чекбоксы
        for key, values in request.POST.lists():
            if key.startswith("perm_"):
                role_id = key.split("_", 1)[1]
                try:
                    role = Role.objects.get(pk=role_id)
                except Role.DoesNotExist:
                    continue
                role.permissions.set(values)
        messages.success(request, "Изменения сохранены ✅")  # ✅ теперь ок
        return redirect("adminpanel:role_matrix")


class RoleEditView(UpdateView):
    """
    Опционально: быстрый экран редактирования одной роли.
    Выводит те же чекбоксы, но только для одной роли.
    """

    model = Role
    fields = ["name", "permissions"]
    template_name = "adminpanel/roles/edit.html"
    success_url = reverse_lazy("adminpanel:role_matrix")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["perms"] = Permission.objects.order_by("name")
        return ctx


def dashboard(request):
    return render(request, "adminpanel/placeholder.html", {"title": "Дашборд"})


def cashdesk(request):
    return render(request, "adminpanel/placeholder.html", {"title": "Касса"})


def pay_receipts(request):
    return render(
        request, "adminpanel/placeholder.html", {"title": "Квитанции на оплату"}
    )


def accounts(request):
    return render(request, "adminpanel/placeholder.html", {"title": "Лицевые счета"})


def apartments(request):
    return render(request, "adminpanel/placeholder.html", {"title": "Квартиры"})


def owners(request):
    return render(
        request, "adminpanel/placeholder.html", {"title": "Владельцы квартир"}
    )


def houses(request):
    return render(request, "adminpanel/placeholder.html", {"title": "Дома"})


def messages1(request):
    return render(request, "adminpanel/placeholder.html", {"title": "Сообщения"})


def requests(request):
    return render(
        request, "adminpanel/placeholder.html", {"title": "Заявки вызова мастера"}
    )


def meters(request):
    return render(
        request, "adminpanel/placeholder.html", {"title": "Показания счётчиков"}
    )


def site(request):
    return render(
        request, "adminpanel/placeholder.html", {"title": "Управление сайтом"}
    )


def settings(request):
    return render(
        request, "adminpanel/placeholder.html", {"title": "Настройки системы"}
    )


def profile(request):
    return render(
        request, "adminpanel/placeholder.html", {"title": "Профиль администратора"}
    )
