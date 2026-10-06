from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PurchaseForm, PurchaseItemForm
from .models import Purchase, PurchaseItem

from django.forms import inlineformset_factory


PurchaseItemFormSet = inlineformset_factory(
    Purchase,
    PurchaseItem,
    form=PurchaseItemForm,
    extra=1,
    can_delete=True,
)


@login_required
def purchase_list(request):
    purchases = Purchase.objects.select_related(
        "supplier",
        "created_by",
    )

    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    if query:
        purchases = purchases.filter(
            Q(invoice_number__icontains=query)
            | Q(supplier__name__icontains=query)
        )

    if status in Purchase.Status.values:
        purchases = purchases.filter(status=status)

    return render(
        request,
        "purchases/purchase_list.html",
        {
            "purchases": purchases,
            "query": query,
            "selected_status": status,
            "status_choices": Purchase.Status.choices,
        },
    )


@login_required
def purchase_create(request):

    if request.method == "POST":
        form = PurchaseForm(request.POST)
        formset = PurchaseItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():

            with transaction.atomic():
                purchase = form.save(commit=False)
                purchase.created_by = request.user
                purchase.status = Purchase.Status.DRAFT
                purchase.save()

                formset.instance = purchase
                formset.save()

                purchase.calculate_total()

            messages.success(
                request,
                f"Purchase {purchase.invoice_number} created successfully.",
            )

            return redirect(
                "purchases:purchase_detail",
                pk=purchase.pk,
            )

    else:
        form = PurchaseForm()
        form.fields["purchase_date"].initial = None

        formset = PurchaseItemFormSet()

    return render(
        request,
        "purchases/purchase_form.html",
        {
            "form": form,
            "formset": formset,
            "is_edit": False,
        },
    )


@login_required
def purchase_update(request, pk):

    purchase = get_object_or_404(
        Purchase,
        pk=pk,
    )

    if purchase.status != Purchase.Status.DRAFT:
        messages.error(
            request,
            "Only draft purchases can be edited.",
        )
        return redirect(
            "purchases:purchase_detail",
            pk=purchase.pk,
        )

    if request.method == "POST":

        form = PurchaseForm(
            request.POST,
            instance=purchase,
        )

        formset = PurchaseItemFormSet(
            request.POST,
            instance=purchase,
        )

        if form.is_valid() and formset.is_valid():

            with transaction.atomic():

                purchase = form.save()

                formset.instance = purchase
                formset.save()

                purchase.calculate_total()

            messages.success(
                request,
                "Purchase updated successfully.",
            )

            return redirect(
                "purchases:purchase_detail",
                pk=purchase.pk,
            )

    else:
        form = PurchaseForm(
            instance=purchase,
        )

        formset = PurchaseItemFormSet(
            instance=purchase,
        )

    return render(
        request,
        "purchases/purchase_form.html",
        {
            "form": form,
            "formset": formset,
            "purchase": purchase,
            "is_edit": True,
        },
    )


@login_required
def purchase_detail(request, pk):

    purchase = get_object_or_404(
        Purchase.objects.select_related(
            "supplier",
            "created_by",
        ).prefetch_related(
            "items__product",
        ),
        pk=pk,
    )

    return render(
        request,
        "purchases/purchase_detail.html",
        {
            "purchase": purchase,
        },
    )


@login_required
@require_POST
def purchase_receive(request, pk):

    purchase = get_object_or_404(
        Purchase,
        pk=pk,
    )

    if purchase.status != Purchase.Status.DRAFT:
        messages.error(
            request,
            "This purchase has already been processed.",
        )

        return redirect(
            "purchases:purchase_detail",
            pk=purchase.pk,
        )

    try:
        purchase.receive(request.user)

    except ValidationError as exc:

        messages.error(
            request,
            str(exc),
        )

    else:

        messages.success(
            request,
            f"Purchase {purchase.invoice_number} received successfully. "
            "Stock has been updated.",
        )

    return redirect(
        "purchases:purchase_detail",
        pk=purchase.pk,
    )