from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from mailing.models import Mailing, MailingAttempt


class Command(BaseCommand):
    help = "Send scheduled mailings"

    def handle(self, *args, **options):
        now = timezone.now()
        mailings = Mailing.objects.filter(
            is_active=True, status="started", start_time__lte=now, end_time__gte=now
        )

        for mailing in mailings:
            for client in mailing.clients.all():
                try:
                    send_mail(
                        mailing.message.subject,
                        mailing.message.body,
                        "noreply@mailingservice.com",
                        [client.email],
                        fail_silently=False,
                    )

                    MailingAttempt.objects.create(
                        mailing=mailing,
                        status="success",
                        server_response="Email sent successfully",
                    )

                except Exception as e:
                    MailingAttempt.objects.create(
                        mailing=mailing, status="failure", server_response=str(e)
                    )

        self.stdout.write(self.style.SUCCESS("Mailings processed successfully"))
