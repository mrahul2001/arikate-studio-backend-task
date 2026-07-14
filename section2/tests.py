from unittest.mock import patch

from celery.exceptions import Retry
from django.test import TestCase
from rest_framework.test import APIClient

from .models import EmailJob
from .tasks import send_email_task


class EmailQueueTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    @patch("section2.rate_limiter.acquire_token", return_value=True)
    @patch("section2.email_service.EmailService.send")
    def test_email_sent_successfully(
        self,
        mock_send,
        mock_token,
    ):

        job = EmailJob.objects.create(
            recipient="test@test.com",
            subject="Hello",
            body="Testing",
        )

        send_email_task(job.id)

        job.refresh_from_db()

        self.assertEqual(
            job.status,
            EmailJob.Status.SUCCESS,
        )

        mock_send.assert_called_once()

    @patch("section2.rate_limiter.acquire_token", return_value=True)
    @patch("section2.email_service.EmailService.send")
    def test_retry_on_provider_failure(
        self,
        mock_send,
        mock_token,
    ):

        mock_send.side_effect = Exception("SMTP Down")

        job = EmailJob.objects.create(
            recipient="retry@test.com",
            subject="Retry",
            body="Retry",
        )

        with self.assertRaises(Exception):
            send_email_task(job.id)

        job.refresh_from_db()

        self.assertEqual(job.retry_count, 1)

    @patch("section2.rate_limiter.acquire_token", return_value=True)
    @patch("section2.email_service.EmailService.send")
    def test_dead_letter_after_max_retry(
        self,
        mock_send,
        mock_token,
    ):

        mock_send.side_effect = Exception()

        job = EmailJob.objects.create(
            recipient="dead@test.com",
            subject="Dead",
            body="Dead",
            retry_count=5,
        )

        send_email_task(job.id)

        job.refresh_from_db()

        self.assertEqual(
            job.status,
            EmailJob.Status.DEAD,
        )

    @patch("section2.rate_limiter.acquire_token")
    def test_rate_limit(self, mock_token):

        mock_token.side_effect = (
            [True] * 200 +
            [False] * 300
        )

        allowed = 0
        blocked = 0

        for _ in range(500):

            if mock_token():
                allowed += 1
            else:
                blocked += 1

        self.assertEqual(
            allowed,
            200,
        )

        self.assertEqual(
            blocked,
            300,
        )

    @patch("section2.tasks.send_email_task.delay")
    def test_submit_500_jobs(self, mock_delay):

        for i in range(500):

            response = self.client.post(
                "/api/email/",
                {
                    "recipient": f"user{i}@mail.com",
                    "subject": "Hello",
                    "body": "Testing",
                },
                format="json",
            )

            self.assertEqual(
                response.status_code,
                202,
            )

        self.assertEqual(
            EmailJob.objects.count(),
            500,
        )

        self.assertEqual(
            mock_delay.call_count,
            500,
        )