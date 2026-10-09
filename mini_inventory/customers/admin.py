
from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "email",
        "opening_balance",
        "credit_limit",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "phone", "email")
    list_editable = ("is_active",)
    readonly_fields = ("created_at", "updated_at")