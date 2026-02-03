import json
from django.shortcuts import render, get_object_or_404
from django.db.models import (
    Q,
    OuterRef,
    Subquery,
    Min,
    F,
    Case,
    When,
    Value,
    BooleanField,
)
from medicines.models import Batch
from decimal import Decimal
from billing.services import summary, create_invoice
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Customer, InvoiceItem, Invoice, Staff
from django.core.exceptions import ValidationError
from django.utils.timezone import now
import logging
import traceback


logger = logging.getLogger(__name__)


# helper function
def recalculate_totals(request, cart):
    subtotal = Decimal(0)
    total_tax = Decimal(0)
    grand_total = Decimal(0)

    for str_id, item in cart.items():
        base, tax, line_tot = summary(item)
        subtotal += base
        total_tax += tax
        grand_total += line_tot

    # Update Session
    request.session["subtotal"] = float(subtotal)
    request.session["tax_total"] = float(total_tax)
    request.session["grand_total"] = float(grand_total)
    request.session.modified = True

    return subtotal, total_tax, grand_total


# 1. Main POS Page
def pos_billing_page(request):
    cart = request.session.get("cart", {})
    subtotal = request.session.get("subtotal", 0.0)
    tax_total = request.session.get("tax_total", 0.0)
    grand_total = request.session.get("grand_total", 0.0)
    return render(
        request,
        "billing/pos_billing_page.html",
        {
            "cart": cart,
            "subtotal": subtotal,
            "tax_total": tax_total,
            "grand_total": grand_total,
        },
    )


# 2. Search Suggestions (HTMX)


def search_medicine(request):
    query = request.GET.get("search", "")

    if len(query) < 2:
        return render(request, "billing/partials/search_results.html", {"batches": []})

    earliest_expiry_subquery = (
        Batch.objects.filter(
            medicine=OuterRef("medicine"),
            is_active=True,
            current_quantity__gt=0,
            expiration_date__gte=now().date(),
        )
        .values("medicine")
        .annotate(min_expiry=Min("expiration_date"))
        .values("min_expiry")[:1]  # ⭐ IMPORTANT
    )

    batches = (
        Batch.objects.filter(
            Q(medicine__name__icontains=query) | Q(medicine__barcode__icontains=query),
            is_active=True,
            current_quantity__gt=0,
            expiration_date__gte=now().date(),
        )
        .select_related("medicine")
        .annotate(
            earliest_expiry=Subquery(earliest_expiry_subquery),
            is_soonest_expiry=Case(
                When(expiration_date=F("earliest_expiry"), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
        )
    ).order_by(
        "-is_soonest_expiry",  # True first
        "expiration_date",  # Then by date
    )[:10]

    return render(request, "billing/partials/search_results.html", {"batches": batches})


# 3. Add to Cart (HTMX)
def add_to_cart(request):
    batch_id = request.POST.get("batch_id")
    batch = get_object_or_404(Batch, id=batch_id)
    cart = request.session.get("cart", {})
    str_id = str(batch_id)

    if str_id in cart:
        # Increment quantity if exists
        cart[str_id]["quantity"] += 1
        cart[str_id]["total"] = float(cart[str_id]["price"]) * cart[str_id]["quantity"]
    else:
        # Add new item
        cart[str_id] = {
            "name": batch.medicine.name,
            "batch_number": batch.batch_number,
            "expiry_date": batch.expiration_date.isoformat()
            if batch.expiration_date
            else None,
            "price": float(batch.sale_price),
            "gst": float(batch.medicine.gst_percent)
            if batch.medicine.gst_percent is not None
            else 0.0,
            "quantity": 1,
            "total": float(batch.sale_price),
        }

    request.session["cart"] = cart
    request.session.modified = True

    sub, tax, grand = recalculate_totals(request, cart)
    # 1. Render ONLY the Cart Area
    # This ensures it fits perfectly into #cart-area without breaking the DOM
    cart_html = render_to_string(
        "billing/partials/cart_area.html", {"cart": cart}, request=request
    )

    response = HttpResponse(cart_html)

    # 2. Send a Trigger to the frontend
    # This tells main.html to fire the 'update-summary' event
    response["HX-Trigger"] = "update-summary"

    return response


def remove_from_cart(request):
    batch_id = request.POST.get("batch_id")
    cart = request.session.get("cart", {})
    str_id = str(batch_id)

    # 1. Remove Item Logic
    if str_id in cart:
        del cart[str_id]
        request.session["cart"] = cart
        request.session.modified = True

    # 2. Recalculate Totals (CRITICAL: Keeps session data correct)
    # We don't use the return values here, but this function updates
    # request.session['subtotal'], etc., which the Sidebar needs.
    recalculate_totals(request, cart)

    # 3. Render ONLY the Cart Area
    # This ensures the response is just the list of items, no extra summary blocks.
    cart_html = render_to_string(
        "billing/partials/cart_area.html", {"cart": cart}, request=request
    )

    response = HttpResponse(cart_html)

    # 4. Trigger the Sidebar Update
    # This matches the hx-trigger="update-summary" in your main.html
    response["HX-Trigger"] = "update-summary"

    return response


# update cart quantity
def update_cart_quantity(request):
    batch_id = request.POST.get("batch_id")
    action = request.POST.get("action")
    cart = request.session.get("cart", {})
    str_id = str(batch_id)

    # 1. Update Logic (Keep exactly as is)
    if str_id in cart:
        if action == "increment":
            cart[str_id]["quantity"] += 1
        elif action == "decrement" and cart[str_id]["quantity"] > 1:
            cart[str_id]["quantity"] -= 1

        cart[str_id]["total"] = float(cart[str_id]["price"]) * cart[str_id]["quantity"]

    request.session["cart"] = cart
    request.session.modified = True

    # 2. Recalculate Totals (Keep this!)
    # This updates the session variables so the sidebar can read them later.
    recalculate_totals(request, cart)

    # 3. Render ONLY the Cart HTML
    # This ensures the response fits perfectly into #cart-area without duplicates.
    cart_html = render_to_string(
        "billing/partials/cart_area.html", {"cart": cart}, request=request
    )

    response = HttpResponse(cart_html)

    # 4. Trigger the Sidebar Update
    # This tells the frontend: "I updated the cart, now you go refresh the summary."
    response["HX-Trigger"] = "update-summary"

    return response


# summary section
def get_cart_summary(request):
    subtotal = request.session.get("subtotal", 0.0)
    tax_total = request.session.get("tax_total", 0.0)
    grand_total = request.session.get("grand_total", 0.0)

    return render(
        request,
        "billing/partials/summary_area.html",
        {"subtotal": subtotal, "tax_total": tax_total, "grand_total": grand_total},
    )


# Customer Model-Load search inerface


def customer_modal_view(request):
    return render(request, "billing/partials/customers/customer_modal.html")


# search existing customer


def search_customer(request):
    query = request.GET.get("q", "").strip()

    print(f"SEARCH DEBUG: User typed -> '{query}'")

    if len(query) >= 1:
        customers = Customer.objects.filter(
            # ERROR WAS HERE: Changed 'phone__icontains' to 'phone_number__icontains'
            Q(name__icontains=query) | Q(phone_number__icontains=query)
        )[:5]
    else:
        customers = []

    return render(
        request,
        "billing/partials/customers/customer_results.html",
        {"customers": customers},
    )


# Creating New Customer


def create_customer(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")

        if Customer.objects.filter(phone_number=phone).exists():
            return HttpResponse(
                '<div class="alert alert-danger">Customer with this phone already exists!</div>'
            )

        customer = Customer.objects.create(name=name, phone_number=phone, email=email)

        request.session["customer_id"] = customer.id
        request.session["customer_name"] = customer.name
        request.session.modified = True

        new_button_html = render(
            request, "billing/partials/customers/customer_selected_button.html"
        ).content.decode("utf-8")

        response_html = f"""
        <div id="customer-section" hx-swap-oob="true">
            {new_button_html}
        </div>
        """
        response = HttpResponse(response_html)
        response["HX-Trigger"] = json.dumps({"closeModal": True})
        return response


# views.py
def select_customer(request, customer_id):
    customer = Customer.objects.get(id=customer_id)

    request.session["customer_id"] = customer.id
    request.session["customer_name"] = customer.name

    # VERY IMPORTANT
    request.session.save()

    html = render(
        request,
        "billing/partials/customers/customer_selected_button.html",
        {"customer_name": customer.name},
    ).content.decode()

    response = HttpResponse(html)

    # Close modal
    response["HX-Trigger"] = "closeModal"

    return response


def remove_customer(request):
    # Remove only customer-related session keys
    request.session.pop("customer_id", None)
    request.session.pop("customer_name", None)

    request.session.modified = True  # Force save

    html = render(
        request,
        "billing/partials/customers/customer_selected_button.html",
        {"customer_name": None},
    ).content.decode()

    return HttpResponse(html)


def get_customer_section(request):
    return render(
        request,
        "billing/partials/customers/customer_selected_button.html",
        {"customer_name": request.session.get("customer_name")},
    )


logger = logging.getLogger(__name__)


def checkout_view(request):
    if request.method != "POST":
        return render(
            request,
            "billing/partials/invoice/error_popup.html",
            {"message": "Invalid request"},
            status=400,
        )

    payment_mode = request.POST.get("payment_mode", "CASH")

    # --- Staff / Customer / Invoice Logic (Keep as is) ---
    try:
        staff = Staff.objects.get(id=1)
    except Staff.DoesNotExist:
        return render(
            request,
            "billing/partials/invoice/error_popup.html",
            {"message": "No staff found."},
            status=500,
        )

    cart = request.session.get("cart", {})
    if not cart:
        return render(
            request,
            "billing/partials/invoice/error_popup.html",
            {"message": "Cart is empty"},
            status=400,
        )

    customer_id = request.session.get("customer_id")
    customer = None
    if customer_id:
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return render(
                request,
                "billing/partials/invoice/error_popup.html",
                {"message": "Customer not found"},
                status=400,
            )

    try:
        invoice = create_invoice(
            user=staff,
            cart_items=cart,
            customer=customer,
            payment_method=payment_mode,
        )
    except ValidationError as ve:
        return render(
            request,
            "billing/partials/invoice/error_popup.html",
            {"message": str(ve)},
            status=400,
        )
    except Exception as e:
        logger.error("CHECKOUT FAILED", exc_info=True)
        return render(
            request,
            "billing/partials/invoice/error_popup.html",
            {"message": "Internal Error"},
            status=500,
        )

    # --- Success Handling ---

    # 1. Clear Session
    request.session["cart"] = {}
    request.session.modified = True

    # 2. Prepare Main Response (The Popup)
    items = InvoiceItem.objects.filter(invoice=invoice)
    popup_html = render_to_string(
        "billing/partials/invoice/invoice_popup.html",
        {"invoice": invoice, "items": items, "payment_mode": payment_mode},
        request=request,
    )

    # 3. Prepare OOB Update: Clear the Cart List in the background
    empty_cart_html = render_to_string(
        "billing/partials/cart_area.html", {"cart": {}}, request=request
    )
    empty_cart_oob = f'<div id="cart-area" hx-swap-oob="true">{empty_cart_html}</div>'

    # 4. Construct Response
    response = HttpResponse(popup_html + empty_cart_oob)

    # 5. Trigger 'update-summary' so the sidebar totals drop to 0.00
    response["HX-Trigger"] = "update-summary"

    return response


def print_invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items = InvoiceItem.objects.filter(invoice=invoice).select_related(
        "medicine", "batch"
    )
    return render(
        request,
        "billing/print_invoice.html",
        {
            "invoice": invoice,
            "items": items,
        },
    )


# views.py


def clear_cart(request):
    # 1. Empty the cart in session
    request.session["cart"] = {}
    request.session.modified = True

    # 2. Reset totals (optional, but good practice)
    # recalculate_totals(request, {}) # If you use this helper

    # 3. Trigger the summary to update (to show 0.00)
    response = render(request, "billing/partials/cart_area.html", {"cart": {}})
    response["HX-Trigger"] = "update-summary"
    return response
