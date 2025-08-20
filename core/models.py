from django.contrib.auth.models import AbstractUser
from django.db import models


class Permission(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name="roles")

    def __str__(self):
        return self.name


class User(AbstractUser):
    patronymic = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    telegram = models.CharField(max_length=100, blank=True)
    viber = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    role = models.ForeignKey(
        "core.Role", on_delete=models.SET_NULL, null=True, blank=True
    )
