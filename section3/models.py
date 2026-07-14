from django.db import models

from .tenant_context import get_current_tenant


class Tenant(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    def __str__(self):
        return self.name


class TenantQuerySet(models.QuerySet):
    def for_current_tenant(self):
        tenant = get_current_tenant()

        if tenant is None:
            return self.none()

        return self.filter(tenant=tenant)


class TenantManager(models.Manager):
    def get_queryset(self):
        return TenantQuerySet(self.model, using=self._db).for_current_tenant()

class Order(models.Model):

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
    )

    customer_name = models.CharField(
        max_length=100,
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    objects = TenantManager()

    def __str__(self):
        return self.customer_name