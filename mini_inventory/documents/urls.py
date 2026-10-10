from django.urls import path
from . import views

app_name = "documents"

urlpatterns = [
    path("purchases/",
        views.document_list,
        {"document_type": "purchase"},
        name="purchase_list",
    ),
    path(
        "purchases/add/",
        views.document_create,
        {"document_type": "purchase"},
        name="purchase_create",
    ),

    path("sales/",
        views.document_list,
        {"document_type": "sale"},
        name="sale_list",
    ),

    path("sales/add/",
        views.document_create,
        {"document_type": "sale"},
        name="sale_create",
    ),

    path("<int:pk>/", views.document_detail, name="document_detail"),
    path("<int:pk>/edit/", views.document_update, name="document_update"),
    path(
        "<int:pk>/complete/",
        views.complete_document,
        name="complete_document",
    ),

    path(
        "<int:pk>/invoice/",
        views.invoice_print,
        name="invoice_print",
    ),


]
