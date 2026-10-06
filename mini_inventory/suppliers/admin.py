from django.contrib import admin

from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "contact_person",
        "phone",
        "email",
        "is_active",
    )

    search_fields = (
        "name",
        "phone",
        "email",
        "contact_person",
    )

    list_filter = ("is_active",)