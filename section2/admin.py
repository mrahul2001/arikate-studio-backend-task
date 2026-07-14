from django.contrib import admin

from .models import EmailJob


@admin.register(EmailJob)
class EmailJobAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "recipient",
        "status",
        "retry_count",
        "created_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "recipient",
    )