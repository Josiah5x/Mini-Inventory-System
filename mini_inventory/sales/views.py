from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.contrib import messages


from documents.models import OrderDocument


from documents import views as document_views






from datetime import date

from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone

from documents.models import OrderDocument
from documents.forms import OrderItemFormSet
from products.models import Product

from .forms import SaleDocumentForm


@login_required
def sale_create(request):
    today = timezone.localdate()

    if request.method == "POST":
        form = SaleDocumentForm(request.POST)
        formset = OrderItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    document = form.save(commit=False)

                    document.document_type = (
                        OrderDocument.DocumentType.SALE
                    )
                    document.status = OrderDocument.Status.DRAFT
                    document.created_by = request.user

                    # Generate a yearly invoice number.
                    year = str(today.year)
                    document.doc_code = "INV"
                    document.doc_year = year

                    existing_numbers = (
                        OrderDocument.objects.filter(
                            doc_code="INV",
                            doc_year=year,
                        )
                        .values_list("doc_num", flat=True)
                    )

                    numeric_numbers = [
                        int(number)
                        for number in existing_numbers
                        if number.isdigit()
                    ]

                    next_number = max(numeric_numbers, default=0) + 1
                    document.doc_num = f"{next_number:05d}"

                    # Preserve a selected customer as the display name.
                    if document.customer and not document.customer_name:
                        document.customer_name = document.customer.name

                    document.save()

                    formset.instance = document
                    formset.save()

                    document.calculate_totals()

                messages.success(
                    request,
                    f"Sales invoice {document} was created successfully."
                )
                return redirect(
                    "sales:sale_detail",
                    pk=document.pk,
                )

            except Exception as exc:
                messages.error(
                    request,
                    f"Unable to create the sale: {exc}"
                )
    else:
        form = SaleDocumentForm(initial={
            "doc_date": today,
            "currency": "NGN",
            "tax": 0,
        })
        formset = OrderItemFormSet()



    products = Product.objects.filter(
    is_active=True
    ).order_by("name")

    products_data = [
        {
            "id": product.pk,
            "price": str(product.selling_price),
            "name": product.name,
        }
        for product in products
    ]

    return render(
    request,
    "sales/sale_form.html",
    {
        "form": form,
        "formset": formset,
        "products": products,
        "products_data": products_data,
        "today": today,
    },
)


@login_required
def sale_list(request):
    documents = OrderDocument.objects.filter(
        document_type=OrderDocument.DocumentType.SALE
    ).select_related("customer")

    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")

    if query:
        documents = documents.filter(
            Q(doc_code__icontains=query)
            | Q(doc_num__icontains=query)
            | Q(customer_name__icontains=query)
            | Q(customer__name__icontains=query)
        )

    if status:
        documents = documents.filter(status=status)

    page_obj = Paginator(documents, 10).get_page(
        request.GET.get("page")
    )

    return render(request, "sales/sale_list.html", {
        "documents": page_obj.object_list,
        "page_obj": page_obj,
        "query": query,
        "status": status,
        "status_choices": OrderDocument.Status.choices,
    })
