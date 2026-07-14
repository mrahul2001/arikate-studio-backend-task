from django.urls import path

from .views import enqueue_email

urlpatterns = [
    path("email/", enqueue_email, name="enqueue-email"),
]