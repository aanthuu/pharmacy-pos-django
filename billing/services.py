import uuid
from django.utils import timezone
from datetime import datetime
from medicines.models import Medicine, Batch
from inventory.models import StockMovement, Action
from .models import Invoice, InvoiceItem
from django.db.models import Sum
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal


# function for finding Total quantity of the medicine
def get_available_stock_for_display(medicine_id):
    try:
        medicine = Medicine.objects.get(id=medicine_id)
        total_quantity = (
            medicine.batches.filter(
                current_quantity__gt=0, expiration_date__gte=timezone.now().date()
            ).aggregate(total=Sum("current_quantity"))["total"]
            or 0
        )
        return total_quantity
    except Medicine.DoesNotExist:
        return 0


# allocate batches with quantity based on FIFO
def allocate_stock_fifo(batches, quantity_needed):
    remaining = quantity_needed
    allocations = []
    for batch in batches:
        if remaining <= 0:
            break
        allocate_quantity = min(batch.current_quantity, remaining)
        allocations.append({"batch": batch, "quantity": allocate_quantity})
        remaining -= allocate_quantity

    return allocations


# output:[{'batch': batch_obj, 'qty': 10}, {'batch': batch_obj, 'qty': 5}]


def deduct_stock(allocations, invoice_obj):
    sale_action = Action.objects.get(name="Sale")
    for allocation in allocations:
        batch = allocation["batch"]
        qty = allocation["quantity"]
        batch.current_quantity -= qty
        batch.save()
        StockMovement.objects.create(
            medicine=batch.medicine,
            batch=batch,
            action=sale_action,
            quantity=qty,
            invoice_number=invoice_obj,
        )
    return True


# [{'medicine_id': 1, 'qty': 10}, {'medicine_id': 2, 'qty': 5}]
def create_invoice(user, cart_items, customer):
    with transaction.atomic():
        # 1. Create Invoice
        invoice_id = f"INV{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        invoice = Invoice.objects.create(
            invoice_number=invoice_id,
            customer=customer,
            created_by=user,
            total_amount=0,
            gst_amount=0,
            grand_total=0,
        )

        running_total_amount = Decimal(0)
        running_gst_amount = Decimal(0)

        # 2. Process Cart
        for item in cart_items:
            batches = (
                Batch.objects.select_for_update()
                .filter(
                    medicine_id=item["medicine_id"],
                    current_quantity__gt=0,
                    expiration_date__gte=timezone.now().date(),
                )
                .order_by("expiration_date")
            )
            allocations = allocate_stock_fifo(batches, item["qty"])
            allocated_qty = sum(a["quantity"] for a in allocations)
            if allocated_qty < item["qty"]:
                raise ValidationError(
                    f"Insufficient stock for Medicine ID {item['medicine_id']}. Wanted {item['qty']}, found {allocated_qty}."
                )

            # Execute to Inventory Update
            deduct_stock(allocations, invoice)

            # Create Invoice Items
            for alloc in allocations:
                batch = alloc["batch"]
                medicine = batch.medicine
                qty = alloc["quantity"]

                price = batch.sale_price
                gst_pct = medicine.gst_percent

                base_amount = price * qty
                tax_amount = (base_amount * gst_pct) / Decimal(100)
                line_total = base_amount + tax_amount

                InvoiceItem.objects.create(
                    invoice=invoice,
                    medicine=medicine,
                    batch=batch,
                    quantity=qty,
                    unit_price=price,
                    gst_percent=gst_pct,
                    gst_amount=tax_amount,
                    total_amount=line_total,
                )

                # D. Update Running Totals
                running_total_amount += base_amount
                running_gst_amount += tax_amount

        invoice.total_amount = running_total_amount
        invoice.gst_amount = running_gst_amount
        invoice.grand_total = running_total_amount + running_gst_amount
        invoice.save()

        return invoice
