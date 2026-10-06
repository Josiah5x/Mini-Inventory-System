from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):

    class Unit(models.TextChoices):
        PIECE = "piece", "Piece"
        PACK = "pack", "Pack"
        BOX = "box", "Box"
        CARTON = "carton", "Carton"
        KG = "kg", "Kilogram"
        GRAM = "gram", "Gram"
        LITRE = "litre", "Litre"
        METRE = "metre", "Metre"

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )

    name = models.CharField(max_length=200)

    sku = models.CharField(
        max_length=50,
        unique=True,
    )

    barcode = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
        null=True,
    )

    description = models.TextField(blank=True)

    unit = models.CharField(
        max_length=20,
        choices=Unit.choices,
        default=Unit.PIECE,
    )

    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    stock_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    minimum_stock = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=5,
    )

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.minimum_stock

    @property
    def stock_value(self):
        return self.stock_quantity * self.cost_price

    @property
    def potential_sales_value(self):
        return self.stock_quantity * self.selling_price