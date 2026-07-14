from .models import Tenant
from .tenant_context import (
    set_current_tenant,
    clear_current_tenant,
)


class TenantMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        tenant_name = request.headers.get(
            "X-Tenant"
        )

        tenant = None

        if tenant_name:

            tenant = Tenant.objects.filter(
                name=tenant_name
            ).first()

        set_current_tenant(tenant)

        response = self.get_response(request)

        clear_current_tenant()

        return response