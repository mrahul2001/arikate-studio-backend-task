from django.urls import path

from .views import order_list

urlpatterns = [
    path(
        "tenant/orders/",
        order_list,
        name="tenant-orders",
    ),
]