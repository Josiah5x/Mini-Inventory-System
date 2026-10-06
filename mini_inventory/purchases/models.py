from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db import transaction
from django.core.exceptions import ValidationError


class Purchase(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        RECEIVED = "RECEIVED", "Received"
        CANCELLED = "CANCELLED", "Cancelled"

    invoice_number = models.CharField(
        max_length=100,
        unique=True,
    )

    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.PROTECT,
        related_name="purchases",
    )

    purchase_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    subtotal = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    discount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    note = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_purchases",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.invoice_number

    def calculate_total(self):
        self.subtotal = sum(
            item.total
            for item in self.items.all()
        )

        self.total = max(
            Decimal("0"),
            self.subtotal - self.discount,
        )

        self.save(
            update_fields=[
                "subtotal",
                "total",
                "updated_at",
            ]
        )

    @transaction.atomic
    def receive(self, user):

        if self.status != self.Status.DRAFT:
            raise ValidationError(
                "Only draft purchases can be received."
            )

        items = list(
            self.items.select_related("product")
        )

        if not items:
            raise ValidationError(
                "A purchase must contain at least one item."
            )

        from inventory.models import StockMovement

        for item in items:

            StockMovement.record_movement(
                product_id=item.product_id,
                movement_type=StockMovement.MovementType.STOCK_IN,
                quantity=item.quantity,
                user=user,
                reference=self.invoice_number,
                note=f"Purchase received from {self.supplier.name}",
            )

            # Update product cost price using latest purchase cost.
            item.product.cost_price = item.unit_cost
            item.product.save(
                update_fields=["cost_price"]
            )

        self.calculate_total()

        self.status = self.Status.RECEIVED

        self.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )


class PurchaseItem(models.Model):

    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="purchase_items",
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"