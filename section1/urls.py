from django.urls import path
from .views import order_summary, order_summary_optimized

urlpatterns = [
    path("orders/summary/", order_summary, name="order-summary"),
    path("orders/summary_optimized/", order_summary_optimized, name="order-summary-optimized"),
]