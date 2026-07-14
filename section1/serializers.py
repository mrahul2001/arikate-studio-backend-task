from rest_framework import serializers
from .models import Order


class OrderSummarySerializer(serializers.ModelSerializer):
    customer = serializers.CharField(source="customer.name")
    items = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "items",
            "total",
        ]

    def get_items(self, obj):
        return [
            item.product.name
            for item in obj.items.all()
        ]

    def get_total(self, obj):
        return sum(
            item.product.price * item.quantity
            for item in obj.items.all()
        )