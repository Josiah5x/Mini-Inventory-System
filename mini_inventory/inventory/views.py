from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import redirect, render

from .forms import StockMovementForm
from .models import StockMovement


@login_required
def movement_list(request):
    movements = StockMovement.objects.select_related(
        "product",
        "created_by",
    )

    query = request.GET.get("q", "").strip()
    movement_type = request.GET.get("type", "").strip()

    if query:
        movements = (
            movements.filter(product__name__icontains=query)
            | movements.filter(product__sku__icontains=query)
            | movements.filter(reference__icontains=query)
        )

    if movement_type in StockMovement.MovementType.values:
        movements = movements.filter(movement_type=movement_type)

    paginator = Paginator(movements, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "inventory/movement_list.html",
        {
            "page_obj": page_obj,
            "movements": page_obj.object_list,
            "query": query,
            "selected_type": movement_type,
            "movement_types": StockMovement.MovementType.choices,
        },
    )


@login_required
def movement_create(request):
    if request.method == "POST":
        form = StockMovementForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            try:
                with transaction.atomic():
                    movement = StockMovement.record_movement(
                        product_id=data["product"].pk,
                        movement_type=data["movement_type"],
                        quantity=data["quantity"],
                        user=request.user,
                        reference=data["reference"],
                        note=data["note"],
                    )

            except ValidationError as exc:
                form.add_error(None, exc)

            else:
                messages.success(
                    request,
                    "Stock movement recorded successfully.",
                )
                return redirect("inventory:movement_list")

    else:
        form = StockMovementForm()

    return render(
        request,
        "inventory/movement_form.html",
        {
            "form": form,
        },
    )
