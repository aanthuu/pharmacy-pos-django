from django.db import models
from medicines.models import Medicine, Batch
from decimal import Decimal


# Create your models here.
class Staff(models.Model):
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=100)


class Customer(models.Model):
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.CharField(max_length=200)


class Invoice(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("CASH", "Cash"),
        ("UPI", "UPI"),
        ("CARD", "Card"),
    ]
    PAYMENT_STATUS_CHOICES = [("PAID", "Paid"), ("UNPAID", "Unpaid")]
    invoice_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name="invoices"
    )
    created_by = models.ForeignKey(Staff, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(
        max_length=30, choices=PAYMENT_METHOD_CHOICES, default="CASH"
    )
    payment_status = models.CharField(
        max_length=30, choices=PAYMENT_STATUS_CHOICES, default="UNPAID"
    )

    @property
    def total(self):
        return sum(item.item_total for item in self.items.all())

    @property
    def gst(self):
        return sum(item.gst_amount for item in self.items.all())

    @property
    def grandtotal(self):
        return self.total + self.gst


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="items")
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    @property
    def item_total(self):
        return self.unit_price * self.quantity

    @property
    def gst_amount(self):
        return (self.item_total * self.medicine.gst_percent) / Decimal(100)

    @property
    def grand_item_total(self):
        return self.item_total + self.gst_amount
