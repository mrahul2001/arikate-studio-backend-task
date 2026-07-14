from .models import EmailJob

def move_to_dead_letter(job):

    job.status = EmailJob.Status.DEAD

    job.save(update_fields=["status"])