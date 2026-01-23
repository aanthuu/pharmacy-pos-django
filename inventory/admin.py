from django.contrib import admin
from .models import Action, StockMovement
# Register your models here.


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("created_on", "medicine", "batch", "action")
