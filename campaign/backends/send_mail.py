from campaign.backends.base import BaseBackend


class SendMailBackend(BaseBackend):
    """simple backend which uses Django's built-in mail sending mechanisms"""

    def send_mail(self, email, fail_silently=False):
        """
        Parameters:

        ``email``: an instance of django.core.mail.EmailMessage
        ``fail_silently``: a boolean indicating if exceptions should bubble up

        """
        return email.send(fail_silently=fail_silently)

backend = SendMailBackend()
