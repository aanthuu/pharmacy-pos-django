from django.shortcuts import render
from django.db.models import Sum, Q
from django.utils import timezone
from medicines.models import Medicine, Batch, Category


def inventory_list(request):
    # 1. Get Parameters
    view_type = request.GET.get("view_type", "medicines")  # Default to 'medicines'
    search_query = request.GET.get("search", "").strip()
    category_filter = request.GET.get("category", "")
    status_filter = request.GET.get("status", "")

    today = timezone.now().date()

    # 2. Base QuerySets (Optimized with select_related)
    medicines_qs = (
        Medicine.objects.select_related("brand", "category", "pack_type")
        .all()
        .order_by("name")
    )
    batches_qs = (
        Batch.objects.select_related("medicine", "supplier")
        .all()
        .order_by("expiration_date")
    )

    # 3. Determine Data & Template based on View Type
    items = []
    # Default template is the medicine list
    template_name = "inventory/partials/table_medicines.html"

    if view_type == "batches":
        template_name = "inventory/partials/table_batches.html"
        items = batches_qs

        # Search Batches (Batch Number OR Medicine Name)
        if search_query:
            items = items.filter(
                Q(batch_number__icontains=search_query)
                | Q(medicine__name__icontains=search_query)
            )
        # Filter Batches by Category (via Medicine relationship)
        if category_filter:
            items = items.filter(medicine__category__id=category_filter)

    elif view_type == "alerts":
        template_name = (
            "inventory/partials/table_batches.html"  # Reuse batch table layout
        )
        # Alerts: Low Stock (<10) OR Expired
        items = batches_qs.filter(
            Q(current_quantity__lte=10) | Q(expiration_date__lt=today)
        )
        if search_query:
            items = items.filter(medicine__name__icontains=search_query)

    else:
        # Default: 'medicines' (Master List)
        template_name = "inventory/partials/table_medicines.html"

        # We assume 'medicines' if view_type is unknown
        # Calculate Total Stock by summing batches
        items = medicines_qs.annotate(total_stock=Sum("batches__current_quantity"))

        # Search Medicines (Name OR Brand)
        if search_query:
            items = items.filter(
                Q(name__icontains=search_query) | Q(brand__name__icontains=search_query)
            )
        # Filter Medicines by Category
        if category_filter:
            items = items.filter(category__id=category_filter)

    # 4. Common Status Filter (Applies to all views)
    if status_filter:
        is_active = True if status_filter == "active" else False
        items = items.filter(is_active=is_active)

    # 5. Prepare Context
    context = {
        "items": items,
        "view_type": view_type,
        "today": today,
        "categories": Category.objects.all(),
    }

    # 6. HTMX Response: Return ONLY the SPECIFIC partial file
    if request.headers.get("HX-Request"):
        return render(request, template_name, context)

    # 7. Full Page Response: Load main page (which includes the default partial)
    return render(request, "inventory/inventory_list.html", context)
