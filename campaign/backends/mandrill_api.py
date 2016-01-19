import logging
import mandrill
from django.template import Context
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django import template
from campaign.backends.base import BaseBackend
from campaign.context import MailContext

logger = logging.getLogger('django.campaign')


class MandrillApiBackend(BaseBackend):
    """
    Send your campaigns through the Mandrill Transactional Email Service.

    This backend assumes, that your Mandrill API-Key is configured in::

        settings.MANDRILL_API_KEY

    And you need to change the CAMPAIGN_CONTEXT_PROCESSORS setting. The
    default 'campaign.context_processors.recipient' needs to be removed in
    favour of the 'campaign.context_processors.recipient_dict'!

    If no sending address is specified in the database, the From-Email is
    determined from the following settings in this order::

        settings.MANDRILL_API_FROM_EMAIL  # only used by this backend
        settings.CAMPAIGN_FROM_EMAIL  # used by all backends that support it
        settings.DEFAULT_FROM_EMAIL  # used by django

    You can provide additional values for the API call via::

        settings.MANDRILL_API_SETTINGS

        (Defaults to "{}")

    For example to setup tracking you can set it to::

        MANDRILL_API_SETTINGS = {
            "track_opens": True,
            "track_clicks": True,
            "from_name": "My Project",
            "important": False,
        }

    These settings will override the django-campaign defaults.

    Please note, that all Django-Template constructs in the MailTemplate are
    evaluated only once for all recipients. Personalizations happens at
    Mandrill, where each message is processed with 'merge_vars'.
    It might be a good idea to wrap the merge_var placeholders in
    `{% if not viewed_online %}` conditionals, otherwise the raw placeholders
    will be displayed in the web-view of the newsletter.

    """
    def send_campaign(self, campaign, fail_silently=False):
        from campaign.models import BlacklistEntry

        subject = campaign.template.subject
        text_template = template.Template(campaign.template.plain)
        if campaign.template.html is not None and campaign.template.html != u"":
            html_template = template.Template(campaign.template.html)
        else:
            html_template = None

        recipients = []
        merge_vars = []

        for recipient_list in campaign.recipients.all():
            for recipient in recipient_list.object_list():
                # never send mail to blacklisted email addresses
                recipient_email = getattr(recipient, recipient_list.email_field_name)
                if not BlacklistEntry.objects.filter(email=recipient_email).count() and not recipient_email in recipients:
                    recipients.append({'email': recipient_email})

                    context = MailContext(recipient)
                    if campaign.online:
                        context.update({'view_online_url': reverse("campaign_view_online", kwargs={'object_id': campaign.pk}),
                                        'site_url': Site.objects.get_current().domain,
                                        'recipient_email': recipient_email})
                    the_merge_vars = []
                    for k, v in context.flatten().iteritems():
                        the_merge_vars.append({'name': k, 'content': v})
                    merge_vars.append({'rcpt': recipient_email, 'vars': the_merge_vars})

        from_email = self.get_from_email(campaign)

        try:
            mandrill_client = mandrill.Mandrill(settings.MANDRILL_API_KEY)
            message = {
             'auto_html': False,
             'auto_text': False,
             'from_email': from_email,
             'important': False,
             'inline_css': False,
             'merge': True,
             'merge_vars': merge_vars,
             'metadata': {'capaign_id': campaign.pk},
             'preserve_recipients': False,
             'subject': subject,
             'text': text_template.render(Context()),
             'to': recipients,
             'track_opens': True,
             'view_content_link': False
            }

            if html_template:
                message['html'] = html_template.render(Context())

            # update data with user supplied values from settings
            message.update(getattr(settings, 'MANDRILL_API_SETTINGS', {}))

            result = mandrill_client.messages.send(message=message, async=True)
            return len(result)

        except mandrill.Error, e:
            logger.error('Mandrill error: %s - %s' % (e.__class__, e))
            if not fail_silently:
                raise e

    def get_from_email(self, campaign):
        if hasattr(settings, 'MANDRILL_API_FROM_EMAIL'):
            from_email = settings.MANDRILL_API_FROM_EMAIL
        else:
            from_email = getattr(settings, 'CAMPAIGN_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)

        try:
            from_email = campaign.newsletter.from_email
        except:
            pass
        return from_email

backend = MandrillApiBackend()
