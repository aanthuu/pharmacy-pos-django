from django.db import models
from django.db.models import Q
from django.utils import timezone


# Brand Model
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    license_number = models.CharField(max_length=30, null=True, blank=True, unique=True)

    def __str__(self):
        return f"{self.name}"


# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.name}"


# PackType Model
class PackType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.name}"


# Medcine Model
class Medicine(models.Model):
    name = models.CharField(max_length=200)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, null=True, blank=True
    )
    strength = models.CharField(max_length=50, null=True, blank=True)
    pack_size = models.PositiveIntegerField()  # e.g., 10
    pack_type = models.ForeignKey(PackType, on_delete=models.PROTECT)
    hsn_code = models.CharField(max_length=20)
    gst_percent = models.DecimalField(max_digits=4, decimal_places=2)
    barcode = models.CharField(unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "brand", "strength", "pack_size", "pack_type"],
                condition=models.Q(barcode__isnull=True),
                name="unique_medicine_variant_if_no_barcode",
            )
        ]

    def __str__(self):
        parts = [self.name]

        if self.strength:
            parts.append(self.strength)

        if self.pack_size and self.pack_type:
            parts.append(f"({self.pack_size} {self.pack_type})")

        if self.brand:
            parts.append(f"- {self.brand}")

        return " ".join(parts)


class Supplier(models.Model):
    name = models.CharField(max_length=200, null=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email_id = models.CharField(max_length=100, null=True, blank=True)
    place = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


# Batch Model
class Batch(models.Model):
    batch_number = models.CharField(max_length=100, null=False)
    medicine = models.ForeignKey(
        Medicine, on_delete=models.PROTECT, related_name="batches"
    )
    initial_quantity = models.PositiveIntegerField()
    current_quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    expiration_date = models.DateField()
    is_active = models.BooleanField(default=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)

    @property
    def is_expired(self):
        return self.expiration_date < timezone.now().date()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["medicine", "batch_number"],
                name="unique_by_medicine_with_batch_number",
            )
        ]
