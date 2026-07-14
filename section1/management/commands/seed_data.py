import random

from django.core.management.base import BaseCommand

from section1.models import Customer, Product, Order, OrderItem


class Command(BaseCommand):
    help = "Seed sample ecommerce data"

    def handle(self, *args, **kwargs):

        if Customer.objects.exists():
            self.stdout.write(self.style.WARNING("Data already exists"))
            return

        customers = []

        for i in range(50):
            customers.append(
                Customer.objects.create(
                    name=f"Customer {i}",
                    email=f"customer{i}@example.com",
                )
            )

        products = []

        for i in range(100):
            products.append(
                Product.objects.create(
                    name=f"Product {i}",
                    price=random.randint(100, 2000),
                )
            )

        for _ in range(300):

            order = Order.objects.create(
                customer=random.choice(customers)
            )

            for _ in range(random.randint(3, 6)):
                OrderItem.objects.create(
                    order=order,
                    product=random.choice(products),
                    quantity=random.randint(1, 5),
                )

        self.stdout.write(
            self.style.SUCCESS("Database seeded successfully.")
        )