from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SupplierForm
from .models import Supplier


@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()

    query = request.GET.get("q", "").strip()

    if query:
        suppliers = suppliers.filter(
            name__icontains=query
        ) | suppliers.filter(
            phone__icontains=query
        ) | suppliers.filter(
            contact_person__icontains=query
        )

    return render(
        request,
        "suppliers/supplier_list.html",
        {
            "suppliers": suppliers,
            "query": query,
        },
    )


@login_required
def supplier_create(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)

        if form.is_valid():
            supplier = form.save()

            messages.success(
                request,
                f"{supplier.name} was created successfully.",
            )

            return redirect("suppliers:supplier_list")
    else:
        form = SupplierForm()

    return render(
        request,
        "suppliers/supplier_form.html",
        {
            "form": form,
            "title": "Add Supplier",
        },
    )


@login_required
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == "POST":
        form = SupplierForm(
            request.POST,
            instance=supplier,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Supplier updated successfully.",
            )

            return redirect("suppliers:supplier_list")
    else:
        form = SupplierForm(instance=supplier)

    return render(
        request,
        "suppliers/supplier_form.html",
        {
            "form": form,
            "supplier": supplier,
            "title": "Edit Supplier",
        },
    )