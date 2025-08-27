from django import forms
from django.forms import formset_factory

from billing.models import PaymentDetails, PaymentItems
from core.models import House
from django.contrib.auth import get_user_model

User = get_user_model()


class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ["house_name", "address"]
        labels = {"house_name": "Название", "address": "Адрес"}
        widgets = {
            "house_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Название"}
            ),
            "address": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Адрес"}
            ),
        }


# ---- Вкладка «Секции»
class SectionItemForm(forms.Form):
    name = forms.CharField(
        label="Название",
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Секция 1"}
        ),
    )


SectionFormSet = formset_factory(SectionItemForm, extra=0, can_delete=True)


# ---- Вкладка «Этажи»
class FloorItemForm(forms.Form):
    number = forms.IntegerField(
        label="Название",  # как в макете
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "1"}),
    )


FloorFormSet = formset_factory(FloorItemForm, extra=0, can_delete=True)


# ---- Вкладка «Пользователи»
class StaffItemForm(forms.Form):
    user = forms.ModelChoiceField(
        label="ФИО",
        queryset=User.objects.filter(is_staff=True).order_by("last_name", "first_name"),
        widget=forms.Select(attrs={"class": "form-select"}),
        required=True,
    )


StaffFormSet = formset_factory(StaffItemForm, extra=0, can_delete=True)


# ---- Изображения (5 слотов)
class GalleryForm(forms.Form):
    img1 = forms.ImageField(label="Изображение #1 (522x350)", required=False)
    img2 = forms.ImageField(label="Изображение #2 (248x160)", required=False)
    img3 = forms.ImageField(label="Изображение #3 (248x160)", required=False)
    img4 = forms.ImageField(label="Изображение #4 (248x160)", required=False)
    img5 = forms.ImageField(label="Изображение #5 (248x160)", required=False)


STATUS_CHOICES = [
    ("new", "Новый"),
    ("active", "Активен"),
    ("disabled", "Отключен"),
]


class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(
        label="Повторить пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    status = forms.ChoiceField(
        label="Статус",
        choices=STATUS_CHOICES,
        initial="new",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "role"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Email (логин)",
            "phone": "Телефон",
            "role": "Роль",
        }

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Пароли не совпадают")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        status = self.cleaned_data.get("status")
        user.is_active = status == "active"
        user.username = f"{user.first_name} {user.last_name}"
        user.set_password(self.cleaned_data["password1"])
        user.is_staff = True
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    is_active = forms.BooleanField(label="Активен", required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "role", "is_active"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Email (логин)",
            "phone": "Телефон",
            "role": "Роль",
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        # гарантируем что это персонал
        user.is_staff = True
        # username уравняем с email, если пусто
        if user.email and (not user.username):
            user.username = user.email
        if commit:
            user.save()
        return user


class PaymentDetailsForm(forms.ModelForm):
    class Meta:
        model = PaymentDetails
        fields = ["name_company", "payment_details"]
        widgets = {
            "name_company": forms.TextInput(attrs={"class": "form-control"}),
            "payment_details": forms.Textarea(
                attrs={"class": "form-control", "rows": 5}
            ),
        }


class PaymentItemForm(forms.ModelForm):
    class Meta:
        model = PaymentItems
        fields = ["name", "operation_type"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "operation_type": forms.Select(
                choices=[
                    ("Приход", "Приход"),
                    ("Расход", "Расход"),
                ],
                attrs={"class": "form-select"},
            ),
        }
