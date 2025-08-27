from django.db import models
from django.conf import settings


class PaymentDetails(models.Model):
    name_company = models.CharField(max_length=100)
    payment_details = models.TextField()

    def __str__(self):
        return self.name_company


class PaymentItems(models.Model):
    name = models.CharField(max_length=100)
    operation_type = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.operation_type})"


class MeasurementUnit(models.Model):
    MeasurementUnit_name = models.CharField(max_length=255)


class Service(models.Model):
    MeasurementUnit = models.ForeignKey(
        "billing.MeasurementUnit", on_delete=models.PROTECT
    )
    Service_name = models.CharField(max_length=255)


class Tariff(models.Model):
    tariff_name = models.CharField(max_length=255)
    tariff_description = models.TextField()
    last_date = models.DateTimeField()


class TariffService(models.Model):
    tariff = models.ForeignKey("billing.Tariff", on_delete=models.PROTECT)
    service = models.ForeignKey("billing.Service", on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=50)


class PersonalAccount(models.Model):
    number = models.IntegerField()
    status = models.BooleanField()
    house = models.ForeignKey("core.House", on_delete=models.PROTECT)
    section = models.ForeignKey("core.Section", on_delete=models.PROTECT)
    flat = models.ForeignKey("core.Flat", on_delete=models.PROTECT)


class Meter(models.Model):
    house = models.ForeignKey("core.House", on_delete=models.PROTECT)
    section = models.ForeignKey("core.Section", on_delete=models.PROTECT)
    flat = models.ForeignKey("core.Flat", on_delete=models.PROTECT)
    personal_account = models.ForeignKey(
        "billing.PersonalAccount", on_delete=models.PROTECT
    )
    service = models.ForeignKey("billing.Service", on_delete=models.PROTECT)
    serial_number = models.CharField(max_length=255)
    installation_date = models.DateField()
    is_active = models.BooleanField()


class MeterReading(models.Model):
    number = models.CharField(max_length=255)
    date = models.DateField()
    meter = models.ForeignKey("billing.Meter", on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=12, decimal_places=3)
    status = models.CharField(max_length=255)


class Invoice(models.Model):
    invoice_number = (
        models.IntegerField()
    )  # исправлено: invoce_number -> invoice_number
    create_date = models.DateField()
    house = models.ForeignKey("core.House", on_delete=models.PROTECT)
    section = models.ForeignKey("core.Section", on_delete=models.PROTECT)
    flat = models.ForeignKey("core.Flat", on_delete=models.PROTECT)
    personal_account = models.ForeignKey(
        "billing.PersonalAccount", on_delete=models.PROTECT
    )
    period_from = models.DateField()
    period_to = models.DateField()
    tariff = models.ForeignKey("billing.Tariff", on_delete=models.PROTECT)
    is_posted = models.BooleanField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)


class InvoiceService(models.Model):  # исправлено: InvoiceSerсvice -> InvoiceService
    invoice = models.ForeignKey(
        "billing.Invoice", on_delete=models.PROTECT
    )  # исправлено: invoce -> invoice
    service = models.ForeignKey("billing.Service", on_delete=models.PROTECT)
    unit = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=50)
    total = models.DecimalField(max_digits=12, decimal_places=2)


class AccountTransaction(models.Model):
    number = models.CharField(max_length=255)
    date = models.DateField()
    type = models.CharField(max_length=255)
    personal_account = models.ForeignKey(
        "billing.PersonalAccount", on_delete=models.PROTECT
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    comment = models.TextField()
    is_approved = models.BooleanField()
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="managed_transactions",
    )
