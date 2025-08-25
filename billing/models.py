from django.db import models


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
