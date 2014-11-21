from django import template
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from campaign.context import MailContext

class BaseBackend(object):
    """base backend for all campaign backends"""

    context_class = MailContext

    def send_campaign(self, campaign, fail_silently=False):
        """
        Does the actual work
        """
        from campaign.models import BlacklistEntry

        from_email = getattr(settings, 'CAMPAIGN_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)
        subject = campaign.template.subject
        text_template = template.Template(campaign.template.plain)
        if campaign.template.html is not None and campaign.template.html != u"":
            html_template = template.Template(campaign.template.html)

        sent = 0
        used_addresses = []
        for recipient_list in campaign.recipients.all():
            for recipient in recipient_list.object_list():
                # never send mail to blacklisted email addresses
                recipient_email = getattr(recipient, recipient_list.email_field_name)
                if not BlacklistEntry.objects.filter(email=recipient_email).count() and not recipient_email in used_addresses:
                    msg = EmailMultiAlternatives(subject, to=[recipient_email,], from_email=from_email)
                    context = self.context_class(recipient)
                    context.update({'recipient_email': recipient_email})
                    if campaign.online:
                        context.update({'view_online_url': reverse("campaign_view_online", kwargs={'object_id': campaign.pk}),
                                        'site_url': Site.objects.get_current().domain})
                    msg.body = text_template.render(context)
                    if campaign.template.html is not None and campaign.template.html != u"":
                        html_content = html_template.render(context)
                        msg.attach_alternative(html_content, 'text/html')
                    sent += self.send_mail(msg, fail_silently)
                    used_addresses.append(recipient_email)
        return sent

    def send_mail(self, email, fail_silently=False):
        raise NotImplementedError
