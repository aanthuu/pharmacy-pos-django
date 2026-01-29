from django.urls import path
from . import views


urlpatterns = [
    path("", views.pos_billing_page, name="pos"),
    path("search-medicine/", views.search_medicine, name="search_medicine"),
    path("add-to-cart/", views.add_to_cart, name="add_to_cart"),
    path("remove-from-cart/", views.remove_from_cart, name="remove_from_cart"),
    path(
        "update-cart-quantity", views.update_cart_quantity, name="update_cart_quantity"
    ),
    path("get-cart-summary/", views.get_cart_summary, name="get_cart_summary"),
    path("customer/modal/", views.customer_modal_view, name="customer_modal_view"),
    path("customer/search/", views.search_customer, name="search_customer"),
    path("customer/create/", views.create_customer, name="create_customer"),
    path(
        "customer/select/<int:customer_id>/",
        views.select_customer,
        name="select_customer",
    ),
    path("customer/remove/", views.remove_customer, name="remove_customer"),
    path(
        "pos/customer-section/", views.get_customer_section, name="get_customer_section"
    ),
    path("checkout/", views.checkout_view, name="checkout"),
    path(
        "invoice/<int:invoice_id>/print/",
        views.print_invoice_view,
        name="print_invoice",
    ),
    path("clear_cart/", views.clear_cart, name="clear_cart"),
]
