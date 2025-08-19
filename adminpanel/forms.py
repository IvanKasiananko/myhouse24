from django import forms
from core.models import User

STATUS_CHOICES = [
    ("new", "Новый"),
    ("active", "Активен"),
    ("disabled", "Отключен"),
]

class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(label="Повторить пароль", widget=forms.PasswordInput(attrs={"class": "form-control"}))
    status = forms.ChoiceField(label="Статус", choices=STATUS_CHOICES, initial="new",
                               widget=forms.Select(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "role"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name":  forms.TextInput(attrs={"class": "form-control"}),
            "email":      forms.EmailInput(attrs={"class": "form-control"}),
            "phone":      forms.TextInput(attrs={"class": "form-control"}),
            "role":       forms.Select(attrs={"class": "form-control"}),
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
        user.is_active = (status == "active")
        user.username = user.email or user.username
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user