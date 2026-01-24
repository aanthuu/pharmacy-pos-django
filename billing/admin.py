from django.contrib import admin
from .models import Staff, Customer, Invoice, InvoiceItem
# Register your models here.


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("name", "position")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone_number")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "customer__name",
        "created_at",
        "payment_method",
        "payment_status",
    )


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = (
        "invoice",
        "medicine",
        "batch",
        "unit_price",
        "quantity",
    )
