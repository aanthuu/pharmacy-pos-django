from django.db import models
from medicines.models import Medicine, Batch
from billing.models import Invoice


# Create your models here.
class Action(models.Model):
    name = models.CharField(max_length=100, unique=True)


class StockMovement(models.Model):
    medicine = models.ForeignKey(
        Medicine, on_delete=models.PROTECT, related_name="stock_movements"
    )
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)
    action = models.ForeignKey(Action, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    invoice_number = models.ForeignKey(Invoice, on_delete=models.PROTECT, null=True)
