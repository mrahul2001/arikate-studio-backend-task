from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer


@api_view(["GET"])
def order_list(request):

    queryset = Order.objects.all()

    serializer = OrderSerializer(
        queryset,
        many=True,
    )

    return Response(serializer.data)