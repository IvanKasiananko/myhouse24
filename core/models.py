from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


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


class House(models.Model):
    house_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)  # исправлено: adress -> address
    staff = models.ManyToManyField(settings.AUTH_USER_MODEL)


class Section(models.Model):
    section_name = models.CharField(max_length=255)
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name="sections")


class Floor(models.Model):
    number = models.IntegerField()
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="floors"
    )


class Flat(models.Model):
    number_flat = models.IntegerField()
    square = models.FloatField()
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name="flats")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    tariff = models.ForeignKey("billing.Tariff", on_delete=models.PROTECT)


class Gallery(models.Model):  # исправлено: Galery -> Gallery
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(upload_to="core/gallery/")
