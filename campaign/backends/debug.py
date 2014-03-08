from django.core.exceptions import ImproperlyConfigured
from campaign.backends.base import BaseBackend


class DebugBackend(BaseBackend):
    def __init__(self):
        msg = ("The DebugBackend no longer exists. To print Emails to the "
               "console use the smtp_backend and set "
               "settings.EMAIL_BACKEND = "
               "'django.core.mail.backends.console.EmailBackend'")
        raise ImproperlyConfigured(msg)

backend = DebugBackend()