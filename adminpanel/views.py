import json
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView,
    TemplateView,
    ListView,
    DeleteView,
)
from django.contrib import messages
from django.db.models import Count
from billing.models import PaymentDetails, PaymentItems
from core.models import User, Role, Permission, House, Section, Gallery, Floor
from .forms import (
    UserCreateForm,
    UserUpdateForm,
    PaymentDetailsForm,
    PaymentItemForm,
    StaffFormSet,
    FloorFormSet,
    SectionFormSet,
    GalleryForm,
    HouseForm,
)


class UsersPageView(TemplateView):
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


class PaymentItemListView(ListView):
    model = PaymentItems
    template_name = "adminpanel/payment_items/payment_items.html"
    context_object_name = "items"


class PaymentItemCreateView(CreateView):
    model = PaymentItems
    form_class = PaymentItemForm
    template_name = "adminpanel/payment_items/payment_items_form.html"
    success_url = reverse_lazy("adminpanel:payment_items_list")


class PaymentItemUpdateView(UpdateView):
    model = PaymentItems
    form_class = PaymentItemForm
    template_name = "adminpanel/payment_items/payment_items_edit.html"
    success_url = reverse_lazy("adminpanel:payment_items_list")

    def form_valid(self, form):
        messages.success(self.request, "Статья сохранена.")
        return super().form_valid(form)


class PaymentItemDeleteView(View):
    success_url = reverse_lazy("adminpanel:payment_items_list")

    def post(self, request, pk):
        item = get_object_or_404(PaymentItems, pk=pk)
        item.delete()
        messages.success(request, "Статья удалена.")
        return redirect(self.success_url)


class HouseListView(ListView):
    template_name = "adminpanel/houses/index.html"
    model = House
    context_object_name = "houses"
    paginate_by = 25

    def get_queryset(self):
        qs = House.objects.all()  # <- убрал annotate(staff_count=...)
        name = self.request.GET.get("name") or ""
        addr = self.request.GET.get("addr") or ""
        if name:
            qs = qs.filter(house_name__icontains=name)
        if addr:
            qs = qs.filter(address__icontains=addr)
        return qs.order_by("id")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["name"] = self.request.GET.get("name", "")
        ctx["addr"] = self.request.GET.get("addr", "")
        return ctx


# ... HouseDetailView и HouseCreateView без изменений ...


# ---------- Редактирование дома (пока: название и адрес)
# class HouseUpdateView(UpdateView):
#     model = House
#     form_class = HouseForm
#     template_name = "adminpanel/houses/edit.html"
#
#     def form_valid(self, form):
#         messages.success(self.request, "Дом сохранён.")
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         return reverse("adminpanel:house_detail", args=[self.object.pk])
class HouseUpdateView(UpdateView):
    model = House
    form_class = HouseForm
    template_name = "adminpanel/houses/create.html"

    # ===== helpers =====
    def _staff_roles_json(self):
        User = get_user_model()
        roles = {
            u.id: (u.role.name if u.role else "")
            for u in User.objects.filter(is_staff=True).select_related("role")
        }
        return json.dumps(roles)

    def _initial_section_names(self, house):
        return [
            {"name": s.section_name}
            for s in Section.objects.filter(house=house).order_by("id")
        ]

    def _initial_floor_numbers(self, house):
        first_sec = Section.objects.filter(house=house).order_by("id").first()
        if not first_sec:
            return []
        nums = list(
            Floor.objects.filter(section=first_sec)
            .order_by("number")
            .values_list("number", flat=True)
        )
        return [{"number": n} for n in nums]

    def _initial_staff(self, house):
        return [{"user": u.id} for u in house.staff.all()]

    # ===== context (GET и при невалидном POST) =====
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        house = self.object

        # === 1) Форма дома (имя/адрес) ===
        # В UpdateView super уже кладёт 'form'. Дадим шаблону и 'house_form',
        # чтобы он мог использовать {{ house_form.* }} одинаково для create/edit.
        form = ctx.get("form") or HouseForm(instance=house)
        ctx.setdefault("house_form", form)

        # === 2) Галерея: URL уже загруженных изображений для превью ===
        imgs = list(Gallery.objects.filter(house=house).order_by("id")[:5])
        ctx["gallery_urls"] = [img.image.url for img in imgs] + [""] * (5 - len(imgs))

        # === 3) Связанные формы, если их не передали при невалидном POST ===
        ctx.setdefault(
            "gallery_form", GalleryForm(prefix="g")
        )  # file inputs нельзя предзаполнить
        ctx.setdefault(
            "sections_fs",
            SectionFormSet(prefix="sec", initial=self._initial_section_names(house)),
        )
        ctx.setdefault(
            "floors_fs",
            FloorFormSet(prefix="fl", initial=self._initial_floor_numbers(house)),
        )
        ctx.setdefault(
            "staff_fs", StaffFormSet(prefix="st", initial=self._initial_staff(house))
        )

        # === 4) Роли для автоподстановки в UI ===
        ctx["staff_roles"] = self._staff_roles_json()

        # Можно оставить, если где-то используешь:
        ctx["house"] = house

        return ctx

    # ===== POST с formsets =====
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        gallery_form = GalleryForm(request.POST, request.FILES, prefix="g")
        sections_fs = SectionFormSet(request.POST, prefix="sec")
        floors_fs = FloorFormSet(request.POST, prefix="fl")
        staff_fs = StaffFormSet(request.POST, prefix="st")

        all_valid = (
            form.is_valid()
            and gallery_form.is_valid()
            and sections_fs.is_valid()
            and floors_fs.is_valid()
            and staff_fs.is_valid()
        )
        if not all_valid:
            messages.error(request, "Исправьте ошибки в форме.")
            context = self.get_context_data(
                form=form,
                gallery_form=gallery_form,
                sections_fs=sections_fs,
                floors_fs=floors_fs,
                staff_fs=staff_fs,
            )
            return self.render_to_response(context)

        # Сохранение
        with transaction.atomic():
            house = form.save()

            # Галерея: если прислан хоть один новый файл — заменяем всю галерею
            new_files = [
                gallery_form.cleaned_data.get(n)
                for n in ["img1", "img2", "img3", "img4", "img5"]
            ]
            if any(new_files):
                Gallery.objects.filter(house=house).delete()
                for f in new_files:
                    if f:
                        Gallery.objects.create(house=house, image=f)

            # Секции и этажи: пересобрать по введённым значениям
            new_section_names = [
                f.cleaned_data["name"]
                for f in sections_fs.forms
                if f.cleaned_data and not f.cleaned_data.get("DELETE")
            ]
            new_floor_numbers = [
                f.cleaned_data["number"]
                for f in floors_fs.forms
                if f.cleaned_data and not f.cleaned_data.get("DELETE")
            ]

            # удалить старые этажи и секции, затем создать новые
            Floor.objects.filter(section__house=house).delete()
            Section.objects.filter(house=house).delete()

            created_sections = [
                Section.objects.create(house=house, section_name=nm)
                for nm in new_section_names
            ]
            for s in created_sections:
                for num in new_floor_numbers:
                    Floor.objects.create(section=s, number=num)

            # Пользователи (M2M)
            users = [
                f.cleaned_data["user"]
                for f in staff_fs.forms
                if f.cleaned_data and not f.cleaned_data.get("DELETE")
            ]
            house.staff.set(users)

        messages.success(request, "Дом сохранён.")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse("adminpanel:house_detail", args=[self.object.pk])


# ---------- Карточка дома
class HouseDetailView(DetailView):
    template_name = "adminpanel/houses/detail.html"
    model = House
    context_object_name = "house"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        house = self.object
        sections = Section.objects.filter(house=house).order_by("id")
        floors_by_section = (
            Floor.objects.filter(section__house=house)
            .values("section_id")
            .annotate(cnt=Count("id"))
            .order_by("section_id")
        )
        floors_per_section = floors_by_section[0]["cnt"] if floors_by_section else 0
        ctx.update(
            {
                "sections_count": sections.count(),
                "floors_per_section": floors_per_section,
                "gallery": Gallery.objects.filter(house=house).order_by("id")[:5],
                "staff": house.staff.select_related("role").all(),
            }
        )
        return ctx


# ---------- Создание дома (одним POST, без ресайза)
class HouseCreateView(View):
    template_name = "adminpanel/houses/create.html"

    def get(self, request):
        from django.contrib.auth import get_user_model
        import json

        User = get_user_model()
        staff_roles = {
            u.id: (u.role.name if u.role else "")
            for u in User.objects.filter(is_staff=True).select_related("role")
        }

        ctx = {
            "house_form": HouseForm(),
            "gallery_form": GalleryForm(prefix="g"),
            "sections_fs": SectionFormSet(prefix="sec"),
            "floors_fs": FloorFormSet(prefix="fl"),
            "staff_fs": StaffFormSet(prefix="st"),
            "staff_roles": json.dumps(staff_roles),
        }
        return render(request, self.template_name, ctx)

    def post(self, request):
        house_form = HouseForm(request.POST)
        gallery_form = GalleryForm(request.POST, request.FILES, prefix="g")
        sections_fs = SectionFormSet(request.POST, prefix="sec")
        floors_fs = FloorFormSet(request.POST, prefix="fl")
        staff_fs = StaffFormSet(request.POST, prefix="st")

        if not all(
            [
                house_form.is_valid(),
                gallery_form.is_valid(),
                sections_fs.is_valid(),
                floors_fs.is_valid(),
                staff_fs.is_valid(),
            ]
        ):
            from django.contrib.auth import get_user_model
            import json

            User = get_user_model()
            staff_roles = {
                u.id: (u.role.name if u.role else "")
                for u in User.objects.filter(is_staff=True).select_related("role")
            }

            messages.error(request, "Исправьте ошибки в форме.")
            return render(
                request,
                self.template_name,
                {
                    "house_form": house_form,
                    "gallery_form": gallery_form,
                    "sections_fs": sections_fs,
                    "floors_fs": floors_fs,
                    "staff_fs": staff_fs,
                    "staff_roles": json.dumps(staff_roles),
                },
            )

        with transaction.atomic():
            # 1) Дом
            house = house_form.save()

            # 2) Галерея — сохраняем как есть (макс. 5 фото)
            slots = ["img1", "img2", "img3", "img4", "img5"]
            for name in slots:
                f = gallery_form.cleaned_data.get(name)
                if f:
                    g = Gallery(house=house)
                    g.image.save(f.name, f, save=True)

            # 3) Секции
            section_names = [
                f.cleaned_data["name"]
                for f in sections_fs.forms
                if f.cleaned_data and not f.cleaned_data.get("DELETE")
            ]
            sections = []
            for nm in section_names:
                sections.append(Section.objects.create(house=house, section_name=nm))

            # 4) Этажи: S секций × F этажей
            floor_numbers = [
                f.cleaned_data["number"]
                for f in floors_fs.forms
                if f.cleaned_data and not f.cleaned_data.get("DELETE")
            ]
            for s in sections:
                for num in floor_numbers:
                    Floor.objects.create(section=s, number=num)

            # 5) Пользователи (M2M staff)
            users = [
                f.cleaned_data["user"]
                for f in staff_fs.forms
                if f.cleaned_data and not f.cleaned_data.get("DELETE")
            ]
            if users:
                house.staff.set(users)

        messages.success(request, "Дом создан.")
        return redirect(reverse("adminpanel:house_detail", args=[house.pk]))


# ---------- Удаление дома
class HouseDeleteView(DeleteView):
    model = House
    template_name = "adminpanel/houses/confirm_delete.html"
    success_url = reverse_lazy("adminpanel:house_index")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            resp = super().delete(request, *args, **kwargs)
            messages.success(request, "Дом удалён.")
            return resp
        except ProtectedError:
            messages.error(request, "Нельзя удалить дом: есть связанные данные.")
            return redirect(reverse("adminpanel:house_detail", args=[self.object.pk]))


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
