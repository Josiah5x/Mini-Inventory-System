from django.contrib import admin

from .models import OrderDocument, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(OrderDocument)
class OrderDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "doc_code",
        "doc_year",
        "doc_num",
        "document_type",
        "doc_date",
        "status",
        "grand_total",
    )

    list_filter = (
        "document_type",
        "status",
        "doc_date",
    )

    search_fields = (
        "doc_num",
        "supplier_name",
        "customer_name",
        "supplier_invoice",
    )

    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "document",
        "product_code",
        "product_qty",
        "product_price",
        "gross_amount",
    )

    search_fields = (
        "product_code",
        "product_description",
    )