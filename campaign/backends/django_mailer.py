from django.core.exceptions import ImproperlyConfigured
from campaign.backends.base import BaseBackend


class DjangoMailerBackend(BaseBackend):
    def __init__(self):
        msg = ("The DjangoMailerBackend no longer exists. To queue and send "
               "Emails with django-mailer use the django-mailer email backend "
               "by setting EMAIL_BACKEND = 'mailer.backend.DbBackend'")
        raise ImproperlyConfigured(msg)

backend = DjangoMailerBackend()
