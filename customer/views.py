from django.shortcuts import render
from django.db.models import Count, Sum, Q
from billing.models import Customer
# I am assuming you have an Invoice model from previous steps.
# If not, remove the 'annotate' lines and use dummy data.


def customer_list(request):
    search_query = request.GET.get("search", "").strip()

    # 1. Base Query: Fetch Customers and Calculate Stats
    # We use 'invoice__grand_total' assuming your Invoice model links to Customer
    customers = Customer.objects.annotate(
        order_count=Count("invoices"), lifetime_value=Sum("invoices__grand_total")
    ).order_by("-id")

    # 2. Search Logic (Name OR Phone)
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) | Q(phone_number__icontains=search_query)
        )

    context = {
        "customers": customers,
    }

    # 3. HTMX: If searching, return ONLY the grid of cards
    if request.headers.get("HX-Request"):
        return render(request, "customer/partials/customer_grid.html", context)

    # 4. Normal Load
    return render(request, "customer/customer_list.html", context)
