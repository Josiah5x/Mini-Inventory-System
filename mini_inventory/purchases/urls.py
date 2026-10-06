from django.urls import path

from . import views


app_name = "purchases"


urlpatterns = [
    path(
        "",
        views.purchase_list,
        name="purchase_list",
    ),

    path(
        "add/",
        views.purchase_create,
        name="purchase_create",
    ),

    path(
        "<int:pk>/",
        views.purchase_detail,
        name="purchase_detail",
    ),

    path(
        "<int:pk>/edit/",
        views.purchase_update,
        name="purchase_update",
    ),

    path(
        "<int:pk>/receive/",
        views.purchase_receive,
        name="purchase_receive",
    ),
]