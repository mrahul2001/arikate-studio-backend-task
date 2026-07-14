from rest_framework import serializers

from .models import EmailJob

class EmailJobSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailJob

        fields = (
            "recipient",
            "subject",
            "body",
        )