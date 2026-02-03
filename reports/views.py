from django.shortcuts import render
from django.db.models import Sum, Count, F, Avg
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta

# Replace with your actual app name if different
from billing.models import Invoice, InvoiceItem


def report_dashboard(request):
    # 1. Date Range (Default: Last 30 Days)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    # Base Queryset: Invoices from last 30 days
    recent_invoices = Invoice.objects.filter(created_at__date__gte=start_date)

    # --- KPI CARD 1: GROSS REVENUE ---
    total_revenue = recent_invoices.aggregate(sum=Sum("grand_total"))["sum"] or 0

    # --- KPI CARD 2: TAX LIABILITY (GST) ---
    # Assuming 'tax_amount' exists on Invoice. If not, we calculate it from items.
    # Logic: Sum of all (item_total - (item_total / 1.12)) roughly, or use your exact field
    # For now, I will assume you store tax. If not, I'll use a flat estimate based on your screenshot context.
    # precise_tax = InvoiceItem.objects.filter(invoice__in=recent_invoices).aggregate(tax=Sum('tax_amount'))['tax'] or 0
    # Let's use a safe fallback if you don't have a direct tax field:
    estimated_tax = float(total_revenue) * 0.12  # Placeholder 12% estimate

    # --- KPI CARD 3: AVG ORDER VALUE ---
    avg_order_value = recent_invoices.aggregate(avg=Avg("grand_total"))["avg"] or 0

    # --- CHART 1: REVENUE TREND (Line Chart) ---
    # Group by Day and Sum Revenue
    daily_revenue = (
        recent_invoices.annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(daily_sum=Sum("grand_total"))
        .order_by("date")
    )

    chart_dates = [entry["date"].strftime("%d/%m") for entry in daily_revenue]
    chart_values = [float(entry["daily_sum"]) for entry in daily_revenue]

    # --- CHART 2: SALES BY CATEGORY (Doughnut Chart) ---
    # We need to join Invoice -> InvoiceItem -> Medicine -> Category
    category_sales = (
        InvoiceItem.objects.filter(invoice__in=recent_invoices)
        .values("medicine__category__name")
        .annotate(total=Sum("total_amount"))
        .order_by("-total")[:5]
    )

    cat_labels = [entry["medicine__category__name"] for entry in category_sales]
    cat_values = [float(entry["total"]) for entry in category_sales]

    context = {
        "total_revenue": total_revenue,
        "tax_liability": estimated_tax,
        "avg_order_value": avg_order_value,
        "chart_dates": chart_dates,
        "chart_values": chart_values,
        "cat_labels": cat_labels,
        "cat_values": cat_values,
    }

    return render(request, "reports/report_dashboard.html", context)
