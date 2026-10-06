from django.contrib import admin

from .models import Purchase, PurchaseItem


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 0
    readonly_fields = ("total",)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):

    list_display = (
        "invoice_number",
        "supplier",
        "purchase_date",
        "status",
        "total",
        "created_by",
    )

    list_filter = (
        "status",
        "purchase_date",
    )

    search_fields = (
        "invoice_number",
        "supplier__name",
    )

    readonly_fields = (
        "subtotal",
        "total",
        "created_by",
        "created_at",
        "updated_at",
    )

    inlines = [PurchaseItemInline]


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):

    list_display = (
        "purchase",
        "product",
        "quantity",
        "unit_cost",
        "total",
    )

    search_fields = (
        "product__name",
        "product__sku",
        "purchase__invoice_number",
    )