from django.contrib import admin
from .models import Medicine, Brand, PackType, Category, Supplier, Batch
# Register your models here.


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("display_name", "barcode", "created_at", "updated_at")
    search_fields = ("name", "brand__name", "strength", "barcode")
    list_filter = ("brand", "pack_type")

    # Custom method for conceptual display
    def display_name(self, obj):
        parts = [obj.name]

        if obj.strength:
            parts.append(obj.strength)

        if obj.pack_size and obj.pack_type:
            parts.append(f"({obj.pack_size} {obj.pack_type})")

        if obj.brand:
            parts.append(f"- {obj.brand}")

        return " ".join(parts)

    display_name.short_description = "Medicine"  # Column header in admin


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("license_number",)
    list_filter = ("is_active",)


@admin.register(PackType)
class PackTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone_number",
        "email_id",
    )
    search_fields = ("name",)


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = (
        "medicine",
        "batch_number",
        "is_expired",
    )
    search_fields = (
        "batch_number",
        "medicine__name",
        "supplier__name",
    )
    list_filter = ("is_active",)
