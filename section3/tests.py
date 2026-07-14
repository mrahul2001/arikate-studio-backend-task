from django.test import TestCase
from rest_framework.test import APIClient

from .models import Tenant, Order
from .tenant_context import (
    set_current_tenant,
    clear_current_tenant,
)


class TenantIsolationTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.tenant_a = Tenant.objects.create(
            name="TenantA"
        )

        self.tenant_b = Tenant.objects.create(
            name="TenantB"
        )

        # Create data for Tenant A
        Order.objects.create(
            tenant=self.tenant_a,
            customer_name="Rahul",
            total=100,
        )

        # Create data for Tenant B
        Order.objects.create(
            tenant=self.tenant_b,
            customer_name="Alice",
            total=200,
        )

    def tearDown(self):
        clear_current_tenant()

    def test_manager_scopes_queryset_for_tenant_a(self):
        """
        Order.objects.all() should automatically
        return only Tenant A's data.
        """
        set_current_tenant(self.tenant_a)

        orders = Order.objects.all()

        self.assertEqual(orders.count(), 1)
        self.assertEqual(
            orders.first().customer_name,
            "Rahul"
        )

    def test_manager_scopes_queryset_for_tenant_b(self):
        """
        Order.objects.all() should automatically
        return only Tenant B's data.
        """
        set_current_tenant(self.tenant_b)

        orders = Order.objects.all()

        self.assertEqual(orders.count(), 1)
        self.assertEqual(
            orders.first().customer_name,
            "Alice"
        )

    def test_objects_all_does_not_bypass_scoping(self):
        """
        Explicitly verify that calling
        Order.objects.all() never returns
        another tenant's data.
        """
        set_current_tenant(self.tenant_a)

        orders = Order.objects.all()

        self.assertEqual(len(orders), 1)

        self.assertNotEqual(
            orders.first().customer_name,
            "Alice"
        )

    def test_without_tenant_returns_empty_queryset(self):
        """
        Without tenant context,
        no data should be returned.
        """
        clear_current_tenant()

        orders = Order.objects.all()

        self.assertEqual(orders.count(), 0)

    def test_api_returns_only_tenant_a_data(self):
        """
        Middleware should resolve the tenant
        from the request header.
        """
        response = self.client.get(
            "/api/tenant/orders/",
            HTTP_X_TENANT="TenantA",
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["customer_name"],
            "Rahul"
        )

    def test_api_returns_only_tenant_b_data(self):
        response = self.client.get(
            "/api/tenant/orders/",
            HTTP_X_TENANT="TenantB",
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["customer_name"],
            "Alice"
        )