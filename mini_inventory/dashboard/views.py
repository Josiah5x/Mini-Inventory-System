
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.shortcuts import render
from django.utils import timezone

from products.models import Product
from documents.models import OrderDocument


@login_required
def dashboard_home(request):
    today = timezone.localdate()

    # Product statistics
    total_products = Product.objects.count()

    low_stock_count = Product.objects.filter(
        stock_quantity__lte=0
    ).count()

    # Also include products that have reached their minimum stock level.
    low_stock_count = Product.objects.filter(
        stock_quantity__lte=0
    ).count()

    # Sales documents that have been completed
    completed_sales = OrderDocument.objects.filter(
        document_type="SALE",
        status="COMPLETED",
    )

    # Completed purchase documents
    completed_purchases = OrderDocument.objects.filter(
        document_type="PURCHASE",
        status="COMPLETED",
    )

    total_sales = (
        completed_sales.aggregate(total=Sum("grand_total"))["total"]
        or Decimal("0.00")
    )

    total_purchases = (
        completed_purchases.aggregate(total=Sum("grand_total"))["total"]
        or Decimal("0.00")
    )

    # Sales for today
    today_sales = (
        completed_sales.filter(doc_date=today)
        .aggregate(total=Sum("grand_total"))["total"]
        or Decimal("0.00")
    )

    # Most recent sales
    recent_sales = completed_sales.order_by(
        "-doc_date", "-created_at"
    )[:10]

    # Products with low or zero stock
    low_stock_count = Product.objects.filter(
    stock_quantity__lte=F("minimum_stock")
    ).count()

    low_stock_products = Product.objects.filter(
        stock_quantity__lte=F("minimum_stock")
    ).order_by("name")[:10]

    context = {
        "today": today,
        "total_products": total_products,
        "total_sales": total_sales,
        "total_purchases": total_purchases,
        "today_sales": today_sales,
        "low_stock_count": low_stock_count,
        "low_stock_products": low_stock_products,
        "recent_sales": recent_sales,
    }

    return render(request, "dashboard/home.html", context)
