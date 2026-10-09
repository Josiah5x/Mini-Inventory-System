
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CustomerForm
from .models import Customer


@login_required
def customer_list(request):
    customers = Customer.objects.all()

    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")

    if query:
        customers = customers.filter(
            Q(name__icontains=query)
            | Q(phone__icontains=query)
            | Q(email__icontains=query)
        )

    if status in ("active", "inactive"):
        customers = customers.filter(
            is_active=(status == "active")
        )

    paginator = Paginator(customers, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "customers/customer_list.html", {
        "page_obj": page_obj,
        "customers": page_obj.object_list,
        "query": query,
        "status": status,
        "total_customers": Customer.objects.count(),
    })


@login_required
def customer_create(request):
    form = CustomerForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        customer = form.save()
        messages.success(
            request,
            f"Customer '{customer.name}' created successfully."
        )
        return redirect("customers:customer_detail", pk=customer.pk)

    return render(request, "customers/customer_form.html", {
        "form": form,
        "page_title": "Add Customer",
    })


@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=customer)

    if request.method == "POST" and form.is_valid():
        customer = form.save()
        messages.success(request, "Customer updated successfully.")
        return redirect("customers:customer_detail", pk=customer.pk)

    return render(request, "customers/customer_form.html", {
        "form": form,
        "customer": customer,
        "page_title": "Edit Customer",
    })


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    documents = customer.order_documents.order_by(
        "-doc_date", "-pk"
    )

    return render(request, "customers/customer_detail.html", {
        "customer": customer,
        "documents": documents,
    })