
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F
from django.utils import timezone


class StockMovement(models.Model):

    class MovementType(models.TextChoices):
        STOCK_IN = "IN", "Stock In"
        STOCK_OUT = "OUT", "Stock Out"
        ADJUSTMENT = "ADJUSTMENT", "Stock Adjustment"

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="stock_movements",
    )

    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices,
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    previous_stock = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    new_stock = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
    )

    note = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="stock_movements",
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at", "-pk"]

    def __str__(self):
        return (
            f"{self.product.name} - "
            f"{self.get_movement_type_display()} - "
            f"{self.quantity}"
        )

    @classmethod
    @transaction.atomic
    def record_movement(
        cls,
        *,
        product_id,
        movement_type,
        quantity,
        user,
        note="",
        reference="",
    ):
        from products.models import Product

        quantity = Decimal(str(quantity))

        if quantity <= 0:
            raise ValidationError(
                "Quantity must be greater than zero."
            )

        product = Product.objects.select_for_update().get(
            pk=product_id
        )

        previous = product.stock_quantity

        if movement_type == cls.MovementType.STOCK_IN:
            new_stock = previous + quantity

        elif movement_type == cls.MovementType.STOCK_OUT:
            new_stock = previous - quantity

            if new_stock < 0:
                raise ValidationError(
                    "Insufficient stock for this transaction."
                )

        elif movement_type == cls.MovementType.ADJUSTMENT:
            # quantity represents the physical count.
            new_stock = quantity
            quantity = abs(new_stock - previous)

            if new_stock == previous:
                raise ValidationError(
                    "The physical count matches current stock."
                )

        else:
            raise ValidationError("Invalid movement type.")

        Product.objects.filter(pk=product.pk).update(
            stock_quantity=F("stock_quantity")
            + (new_stock - previous)
        )

        return cls.objects.create(
            product=product,
            movement_type=movement_type,
            quantity=quantity,
            previous_stock=previous,
            new_stock=new_stock,
            reference=reference,
            note=note,
            created_by=user,
        )