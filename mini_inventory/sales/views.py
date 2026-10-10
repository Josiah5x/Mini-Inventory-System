from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from documents.models import OrderDocument


from documents import views as document_views





@login_required
def sale_create(request):
    return document_views.document_create(request, "sale")


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
