from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from django.contrib import messages

from billing.models import PaymentDetails
from core.models import User, Role, Permission
from .forms import UserCreateForm, UserUpdateForm, PaymentDetailsForm


class UsersPageView1(TemplateView):
    template_name = "adminpanel/users/list_ajax.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["roles"] = Role.objects.order_by("name")
        ctx["users"] = (
            User.objects.select_related("role")
            .filter(is_staff=True)  # только персонал
            .order_by("id")
        )
        return ctx


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


class UserUpdateView(UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "adminpanel/users/edit.html"
    success_url = reverse_lazy("adminpanel:user_list")

    def form_valid(self, form):
        messages.success(self.request, "Пользователь сохранён.")
        return super().form_valid(form)


class UserDeleteView(View):
    success_url = reverse_lazy("adminpanel:user_list")

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk, is_staff=True)
        user.delete()
        messages.success(request, "Пользователь удалён.")
        return redirect(self.success_url)


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
    model = Role
    fields = ["name", "permissions"]
    template_name = "adminpanel/roles/edit.html"
    success_url = reverse_lazy("adminpanel:role_matrix")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["perms"] = Permission.objects.order_by("name")
        return ctx


class PaymentDetailsUpdateView(UpdateView):
    model = PaymentDetails
    form_class = PaymentDetailsForm
    template_name = "adminpanel/requisites.html"
    success_url = reverse_lazy("adminpanel:requisites")

    def get_object(self, queryset=None):
        return PaymentDetails.objects.first()


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
