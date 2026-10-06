from django.urls import path

from . import views


app_name = "products"


urlpatterns = [
    path(
        "",
        views.product_list,
        name="product_list",
    ),

    path(
        "add/",
        views.product_create,
        name="product_create",
    ),

    path(
        "<int:pk>/",
        views.product_detail,
        name="product_detail",
    ),

    path(
        "<int:pk>/edit/",
        views.product_update,
        name="product_update",
    ),

    path(
        "categories/",
        views.category_list,
        name="category_list",
    ),

    path(
        "categories/add/",
        views.category_create,
        name="category_create",
    ),
]