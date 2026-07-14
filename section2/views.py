from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import EmailJob
from .serializers import EmailJobSerializer
from .tasks import send_email_task


@api_view(["POST"])
def enqueue_email(request):

    serializer = EmailJobSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    job = serializer.save()

    send_email_task.delay(job.id)

    return Response(
        {
            "message": "Email queued",
            "job_id": job.id,
        },
        status=202,
    )
