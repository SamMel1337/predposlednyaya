from django.core.mail import send_mail
from django.conf import settings
from .models import MailingAttempt


def send_mailing(mailing):
    """
    Отправляет рассылку и создает записи о попытках
    """
    success_count = 0
    total_count = mailing.clients.count()

    for client in mailing.clients.all():
        try:
            send_mail(
                mailing.message.subject,
                mailing.message.body,
                settings.DEFAULT_FROM_EMAIL,
                [client.email],
                fail_silently=False,
            )

            MailingAttempt.objects.create(
                mailing=mailing,
                status="success",
                server_response="Email sent successfully",
            )
            success_count += 1

        except Exception as e:
            MailingAttempt.objects.create(
                mailing=mailing, status="failure", server_response=str(e)
            )

    return success_count, total_count
