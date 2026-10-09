
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils import timezone


from django.db import models




class OrderDocument(models.Model):

    class DocumentType(models.TextChoices):
        PURCHASE = "PURCHASE", "Purchase"
        SALE = "SALE", "Sales"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    # Document identification
    doc_code = models.CharField(max_length=10)
    doc_year = models.CharField(max_length=4)
    doc_num = models.CharField(max_length=20)

    document_type = models.CharField(
        max_length=10,
        choices=DocumentType.choices,
        default=DocumentType.PURCHASE,
    )

    doc_date = models.DateField(default=timezone.localdate)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    # Supplier information
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.PROTECT,
        related_name="order_documents",
        null=True,
        blank=True,
    )

    supplier_name = models.CharField(
        max_length=255,
        blank=True,
    )

    supplier_invoice = models.CharField(
        max_length=100,
        blank=True,
    )

    # Customer information for sales
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="order_documents",
        null=True,
        blank=True,
    )

    customer_name = models.CharField(
        max_length=255,
        blank=True,
    )

    # Other document details
    currency = models.CharField(max_length=10, default="NGN", blank=True)
    credit_fercility = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    project = models.CharField(max_length=255, blank=True)

    # Financial totals
    subtotal = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_discount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    tax = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    grand_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # Audit fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="order_documents",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["doc_code", "doc_year", "doc_num"],
                name="unique_order_document_number",
            ),
        ]

    def __str__(self):
        return f"{self.doc_code}-{self.doc_year}-{self.doc_num}"

    def calculate_totals(self, save=True):
        items = self.items.all()

        subtotal = items.aggregate(
            amount=Sum("product_amount")
        )["amount"] or Decimal("0.00")

        discount = items.aggregate(
            amount=Sum("discount")
        )["amount"] or Decimal("0.00")

        self.subtotal = subtotal
        self.total_discount = discount
        self.grand_total = max(
            Decimal("0.00"),
            subtotal - discount + self.tax,
        )

        if save:
            self.save(
                update_fields=[
                    "subtotal",
                    "total_discount",
                    "grand_total",
                    "updated_at",
                ]
            )


class OrderItem(models.Model):

    document = models.ForeignKey(
        OrderDocument,
        on_delete=models.CASCADE,
        related_name="items",
    )

    # Link to inventory while retaining the original product code.
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="order_items",
        null=True,
        blank=True,
    )

    product_code = models.CharField(max_length=255)
    product_description = models.TextField(blank=True)
    warehouse = models.CharField(max_length=255, blank=True)

    product_qty = models.DecimalField(
        max_digits=10,
        decimal_places=3,
    )

    product_unit = models.CharField(max_length=10)

    product_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    product_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    percentage_discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    gross_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.product_code

    def save(self, *args, **kwargs):
        if self.document_id and self.document.status != OrderDocument.Status.DRAFT:
            raise ValidationError(
                "Items can only be changed while the document is a draft."
            )

        if self.product_qty <= 0:
            raise ValidationError(
                "Product quantity must be greater than zero."
            )

        if self.product_price < 0:
            raise ValidationError(
                "Product price cannot be negative."
            )

        if not Decimal("0") <= self.percentage_discount <= Decimal("100"):
            raise ValidationError(
                "Discount percentage must be between 0 and 100."
            )

        # Calculate the line amount.
        self.product_amount = (
            self.product_qty * self.product_price
        ).quantize(Decimal("0.01"))

        self.discount = (
            self.product_amount
            * self.percentage_discount
            / Decimal("100")
        ).quantize(Decimal("0.01"))

        self.gross_amount = (
            self.product_amount - self.discount
        ).quantize(Decimal("0.01"))

        if self.product:
            self.product_code = self.product.sku
            self.product_description = self.product.name
            self.product_unit = self.product.unit

        super().save(*args, **kwargs)
        