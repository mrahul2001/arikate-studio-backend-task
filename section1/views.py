from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Order
from .serializers import OrderSummarySerializer


@api_view(["GET"])
def order_summary(request):
    """
    Intentionally inefficient implementation.
    Used to demonstrate N+1 queries.
    """

    orders = Order.objects.all()

    serializer = OrderSummarySerializer(orders, many=True)

    return Response(serializer.data)

@api_view(["GET"])
def order_summary_optimized(request):

    orders = (
        Order.objects
        .select_related("customer")
        .prefetch_related("items__product")
    )

    serializer = OrderSummarySerializer(
        orders,
        many=True
    )

    return Response(serializer.data)