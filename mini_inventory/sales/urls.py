

from django.urls import path
from . import views
from documents import views as document_views

app_name = "sales"

urlpatterns = [
    path("", views.sale_list, name="sale_list"),
    path("add/", views.sale_create, name="sale_create"),
    path(
        "<int:pk>/",
        document_views.document_detail,
        name="sale_detail",
    ),
    path(
        "<int:pk>/edit/",
        document_views.document_update,
        name="sale_update",
    ),
    path(
        "<int:pk>/complete/",
        document_views.complete_document,
        name="sale_complete",
    ),
    path(
        "<int:pk>/invoice/",
        document_views.invoice_print,
        name="sale_invoice",
    ),
]
