from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "is_active",
        "created_at",
    )

    search_fields = ("name",)

    list_filter = ("is_active",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "sku",
        "category",
        "cost_price",
        "selling_price",
        "stock_quantity",
        "minimum_stock",
        "stock_status",
    )

    search_fields = (
        "name",
        "sku",
        "barcode",
    )

    list_filter = (
        "category",
        "unit",
        "is_active",
    )

    def stock_status(self, obj):
        if obj.is_low_stock:
            return "LOW STOCK"

        return "OK"

    stock_status.short_description = "Stock Status"