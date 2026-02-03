from django.shortcuts import render
from django.utils import timezone
from billing.models import Invoice
from medicines.models import Batch
from django.db.models import Sum, Count
from datetime import timedelta


# Create your views here.
def dashboard(request):
    now = timezone.now()
    sales_data = Invoice.objects.filter(created_at__date=now.date()).aggregate(
        total=Sum("grand_total"), count=Count("id")
    )
    sales_today = sales_data["total"] or 0
    invoices_today_count = sales_data["count"] or 0
    low_stock_items = Batch.objects.filter(current_quantity__lt=10)
    expired_items = Batch.objects.filter(
        expiration_date__lt=now.date(), current_quantity__gt=0
    )
    low_stock_list = low_stock_items.order_by("current_quantity")[:3]
    expired_list = expired_items.order_by("expiration_date")[:3]
    recent_invoices = Invoice.objects.all().order_by("-created_at")[:5]
    dates = []
    revenues = []
    # Loop 7 times (from 6 days ago up to today)
    for i in range(6, -1, -1):
        target_date = now.date() - timedelta(days=i)

        # Get sales for that specific day
        day_sales = (
            Invoice.objects.filter(created_at__date=target_date).aggregate(
                total=Sum("grand_total")
            )["total"]
            or 0
        )

        # Add to our lists
        dates.append(target_date.strftime("%d/%m"))  # Format as "30/01"
        revenues.append(float(day_sales))
    context = {
        "sales_today": sales_today,
        "invoices_today_count": invoices_today_count,
        "low_stock_items_count": low_stock_items.count(),
        "expired_items_count": expired_items.count(),
        "low_stock_list": low_stock_list,
        "expired_list": expired_list,
        "chart_dates": dates,
        "chart_revenues": revenues,
        "recent_invoices": recent_invoices,
    }
    return render(request, "dashboard/main_dashboard.html", context)
