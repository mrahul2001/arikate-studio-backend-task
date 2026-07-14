class EmailProviderException(Exception):
    pass


class EmailService:

    @staticmethod
    def send(job):
        """
        Stub email sender.

        During testing we'll mock this method to
        simulate success/failure.
        """
        print(f"Sending email to {job.recipient}")