from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoryForm, ProductForm
from .models import Category, Product


@login_required
def product_list(request):
    products = Product.objects.select_related("category").all()

    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()

    if query:
        products = products.filter(
            name__icontains=query
        ) | products.filter(
            sku__icontains=query
        ) | products.filter(
            barcode__icontains=query
        )

    if category:
        products = products.filter(category_id=category)

    categories = Category.objects.filter(is_active=True)

    return render(
        request,
        "products/product_list.html",
        {
            "products": products,
            "categories": categories,
            "query": query,
            "selected_category": category,
        },
    )


@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save()

            messages.success(
                request,
                f"{product.name} was created successfully."
            )

            return redirect("products:product_list")

    else:
        form = ProductForm()

    return render(
        request,
        "products/product_form.html",
        {
            "form": form,
            "title": "Add Product",
        },
    )


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(
            request.POST,
            request.FILES,
            instance=product,
        )

        if form.is_valid():
            product = form.save()

            messages.success(
                request,
                f"{product.name} was updated successfully."
            )

            return redirect("products:product_list")

    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "products/product_form.html",
        {
            "form": form,
            "product": product,
            "title": "Edit Product",
        },
    )


@login_required
def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        pk=pk,
    )

    return render(
        request,
        "products/product_detail.html",
        {
            "product": product,
        },
    )


@login_required
def category_list(request):
    categories = Category.objects.all()

    return render(
        request,
        "products/category_list.html",
        {
            "categories": categories,
        },
    )


@login_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)

        if form.is_valid():
            category = form.save()

            messages.success(
                request,
                f"{category.name} was created successfully."
            )

            return redirect("products:category_list")

    else:
        form = CategoryForm()

    return render(
        request,
        "products/category_form.html",
        {
            "form": form,
            "title": "Add Category",
        },
    )