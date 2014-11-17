from campaign.backends.base import BaseBackend


class SendMailBackend(BaseBackend):
    """
    Simple backend which uses Django's built-in mail sending mechanisms.

    The From-Email is determined from the following settings in this order::

        settings.CAMPAIGN_FROM_EMAIL  # used by all backends that support it
        settings.DEFAULT_FROM_EMAIL  # used by django

    """

    def send_mail(self, email, fail_silently=False):
        """
        Parameters:

        ``email``: an instance of django.core.mail.EmailMessage
        ``fail_silently``: a boolean indicating if exceptions should bubble up

        """
        return email.send(fail_silently=fail_silently)

backend = SendMailBackend()
