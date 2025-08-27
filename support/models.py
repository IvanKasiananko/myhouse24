from django.conf import settings
from django.db import models


class Message(models.Model):
    Subject = models.CharField(max_length=255)
    Body = models.TextField()
    created_at = models.DateTimeField()
    recipients = models.ManyToManyField(settings.AUTH_USER_MODEL)
    house = models.ForeignKey("core.House", on_delete=models.PROTECT)
    section = models.ForeignKey("core.Section", on_delete=models.PROTECT)
    floor = models.ForeignKey("core.Floor", on_delete=models.PROTECT)
    flat = models.ForeignKey("core.Flat", on_delete=models.PROTECT)
    only_debtors = models.BooleanField()


class MasterRequest(models.Model):
    flat = models.ForeignKey("core.Flat", on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    master_type = models.ForeignKey("core.Role", on_delete=models.PROTECT)
    status = models.CharField(max_length=255)  # ChoiceField на схеме → CharField здесь
    description = models.TextField()
    comment = models.TextField()
    preferred_time = models.DateTimeField()  # исправлено: DateTimeFie -> DateTimeField
    master = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="master_requests",
    )  # staff
