
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from inventory.models import StockMovement
from products.models import Product

from .forms import OrderDocumentForm, OrderItemFormSet
from .models import OrderDocument


def _get_document_type(value):
    if value == "purchase":
        return OrderDocument.DocumentType.PURCHASE
    if value == "sale":
        return OrderDocument.DocumentType.SALE
    raise Http404("Unknown document type.")


@login_required
def document_list(request, document_type):
    doc_type = _get_document_type(document_type)
    documents = OrderDocument.objects.filter(document_type=doc_type)

    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")

    if query:
        documents = documents.filter(
            Q(doc_code__icontains=query)
            | Q(doc_num__icontains=query)
            | Q(supplier_name__icontains=query)
            | Q(customer_name__icontains=query)
            | Q(supplier_invoice__icontains=query)
        )

    if status:
        documents = documents.filter(status=status)

    page_obj = Paginator(documents, 10).get_page(
        request.GET.get("page")
    )

    return render(request, "documents/document_list.html", {
        "documents": page_obj.object_list,
        "page_obj": page_obj,
        "document_type": document_type,
        "document_label": "Purchases" if document_type == "purchase" else "Sales",
        "query": query,
        "status": status,
        "status_choices": OrderDocument.Status.choices,
    })


@login_required
def document_create(request, document_type):
    doc_type = _get_document_type(document_type)

    form = OrderDocumentForm(request.POST or None)
    formset = OrderItemFormSet(
        request.POST or None,
        instance=form.instance,
        prefix="items",
    )

    if request.method == "POST":
        if form.is_valid() and formset.is_valid():
            document = form.save(commit=False)
            document.document_type = doc_type
            document.status = OrderDocument.Status.DRAFT
            document.created_by = request.user
            document.save()

            formset.instance = document
            formset.save()
            document.calculate_totals()

            messages.success(request, "Document saved as draft.")
            return redirect(
                "documents:document_detail", pk=document.pk
            )

    return render(request, "documents/document_form.html", {
        "form": form,
        "formset": formset,
        "document_type": document_type,
        "page_title": "New Purchase" if document_type == "purchase" else "New Sale",
        "is_edit": False,
    })


@login_required
def document_update(request, pk):
    document = get_object_or_404(OrderDocument, pk=pk)

    if document.status != OrderDocument.Status.DRAFT:
        messages.error(request, "Only draft documents can be edited.")
        return redirect("documents:document_detail", pk=document.pk)

    document_type = (
        "purchase"
        if document.document_type == OrderDocument.DocumentType.PURCHASE
        else "sale"
    )

    form = OrderDocumentForm(
        request.POST or None,
        instance=document,
    )
    formset = OrderItemFormSet(
        request.POST or None,
        instance=document,
        prefix="items",
    )

    if request.method == "POST":
        if form.is_valid() and formset.is_valid():
            saved_document = form.save(commit=False)
            saved_document.document_type = document.document_type
            saved_document.save()

            formset.instance = saved_document
            formset.save()
            saved_document.calculate_totals()

            messages.success(request, "Document updated successfully.")
            return redirect(
                "documents:document_detail", pk=saved_document.pk
            )

    return render(request, "documents/document_form.html", {
        "form": form,
        "formset": formset,
        "document": document,
        "document_type": document_type,
        "page_title": "Edit Document",
        "is_edit": True,
    })


@login_required
def document_detail(request, pk):
    document = get_object_or_404(
        OrderDocument.objects.prefetch_related("items__product"),
        pk=pk,
    )

    return render(request, "documents/document_detail.html", {
        "document": document,
        "items": document.items.all(),
        "is_purchase": (
            document.document_type
            == OrderDocument.DocumentType.PURCHASE
        ),
    })


@login_required
@require_POST
def complete_document(request, pk):
    with transaction.atomic():
        document = get_object_or_404(
            OrderDocument.objects.select_for_update(),
            pk=pk,
        )

        if document.status != OrderDocument.Status.DRAFT:
            messages.error(request, "This document has already been processed.")
            return redirect("documents:document_detail", pk=pk)

        items = list(document.items.select_related("product").all())

        if not items:
            messages.error(request, "Add at least one item before processing.")
            return redirect("documents:document_detail", pk=pk)

        is_purchase = (
            document.document_type
            == OrderDocument.DocumentType.PURCHASE
        )

        try:
            for item in items:
                if item.product_id is None:
                    raise ValidationError(
                        f"Select a product for item {item.product_code}."
                    )

                movement_type = (
                    StockMovement.MovementType.STOCK_IN
                    if is_purchase
                    else StockMovement.MovementType.STOCK_OUT
                )

                StockMovement.record_movement(
                    product_id=item.product_id,
                    movement_type=movement_type,
                    quantity=item.product_qty,
                    reference=str(document),
                    note=(
                        f"{'Purchase received' if is_purchase else 'Sale completed'}: "
                        f"{document}"
                    ),
                    created_by=request.user,
                )

                if is_purchase:
                    Product.objects.filter(pk=item.product_id).update(
                        cost_price=item.product_price
                    )

            document.calculate_totals(save=False)
            document.status = OrderDocument.Status.COMPLETED
            document.save(update_fields=[
                "subtotal",
                "total_discount",
                "grand_total",
                "status",
                "updated_at",
            ])

        except (ValidationError, ValueError) as exc:
            message = (
                "; ".join(exc.messages)
                if isinstance(exc, ValidationError)
                else str(exc)
            )
            messages.error(request, message)
            return redirect("documents:document_detail", pk=pk)

    messages.success(
        request,
        "Purchase received and stock updated."
        if is_purchase
        else "Sale completed and stock updated.",
    )
    return redirect("documents:document_detail", pk=pk)