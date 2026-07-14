from celery import shared_task

from .dead_letter import move_to_dead_letter
from .email_service import EmailService
from .models import EmailJob
from .rate_limiter import acquire_token

MAX_RETRIES = 5


@shared_task(bind=True, acks_late=True)
def send_email_task(self, job_id):

    job = EmailJob.objects.get(pk=job_id)

    if job.status == EmailJob.Status.SUCCESS:
        return

    # -------------------------
    # Rate Limiter
    # -------------------------

    if not acquire_token():
        raise self.retry(countdown=5)

    job.status = EmailJob.Status.PROCESSING
    job.save(update_fields=["status"])

    try:

        EmailService.send(job)

        job.status = EmailJob.Status.SUCCESS
        job.save(update_fields=["status"])

    except Exception as exc:

        job.retry_count += 1
        job.save(update_fields=["retry_count"])

        if job.retry_count >= MAX_RETRIES:
            move_to_dead_letter(job)
            return

        delay = 2 ** job.retry_count

        raise self.retry(exc=exc, countdown=delay)