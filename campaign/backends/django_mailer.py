# simple backend using django-mailer to queue and send the mails
from django.conf import settings
from mailer import send_mail

class DjangoMailerBackend(object):
    def send_mail(self, email, fail_silently=False):
        subject = email.subject
        body = email.body
        # django_mailer does not support multi-part messages so we loose the
        # html content
        return send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, email.recipients(), 
                    fail_silently=fail_silently)
                    
backend = DjangoMailerBackend()