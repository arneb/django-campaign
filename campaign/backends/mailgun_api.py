import logging
import json
import requests
from django.template import Context
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django import template
from campaign.backends.base import BaseBackend
from campaign.context import MailContext

logger = logging.getLogger('django.campaign')


class MailgunApiBackend(BaseBackend):
    """
    Send your campaigns through the Mailgun Email Service.

    This backend assumes, that your Mailgun API-Key is configured in::

        settings.MAILGUN_API_KEY

    And you need to change the CAMPAIGN_CONTEXT_PROCESSORS setting. The
    default 'campaign.context_processors.recipient' needs to be removed in
    favour of the 'campaign.context_processors.recipient_dict'!

    If no sending address is specified in the database, the From-Email is
    determined from the following settings in this order::

        settings.MAILGUN_API_FROM_EMAIL  # only used by this backend
        settings.CAMPAIGN_FROM_EMAIL  # used by all backends that support it
        settings.DEFAULT_FROM_EMAIL  # used by django

    You can provide additional values for the API call via::

        settings.MAILGUN_API_SETTINGS

        (Defaults to "{}")

    For example to setup tracking you can set it to::

        MAILGUN_API_SETTINGS = {
            "o:tracking": "yes",
            "o:tracking-opens": "yes",
            "o:tracking-clicks": "yes"
        }

    These settings will override the django-campaign defaults.

    If no sending name is specified in the database, the from header is
    either determined from the CAMPAIGN_FROM_HEADERS setting or only the
    plain email address is used.

    To specify a from-header (with display-name) for a specific address
    the following setting can be used::

        settings.CAMPAIGN_FROM_HEADERS

    Example configuration::

        CAMPAIGN_FROM_HEADERS = {
            "newsletter@example.com": "Example Newsletter <newsletter@example.com>",
            "no-reply@test.com": "Test Sender <no-reply@test.com>"
        }

    These From-Headers are used, when an email is sent with the matching
    address. The setting is optional.

    Please note, that all Django-Template constructs in the MailTemplate are
    evaluated only once for all recipients. Personalizations happens at
    Mailgun, where each message is processed with 'recipient_vars'.
    It might be a good idea to wrap the recipient_vars placeholders in
    `{% if not viewed_online %}` conditionals, otherwise the raw placeholders
    will be displayed in the web-view of the newsletter.

    """
    BATCH_SIZE = 1000

    def send_campaign(self, campaign, fail_silently=False):
        from campaign.models import BlacklistEntry

        subject = campaign.template.subject
        text_template = template.Template(campaign.template.plain)
        if campaign.template.html is not None and campaign.template.html != u"":
            html_template = template.Template(campaign.template.html)
        else:
            html_template = None

        success_count = 0
        recipients = []
        recipient_vars = {}

        for recipient_list in campaign.recipients.all():
            for recipient in recipient_list.object_list():
                # never send mail to blacklisted email addresses
                recipient_email = getattr(recipient, recipient_list.email_field_name)
                if not BlacklistEntry.objects.filter(email=recipient_email).count() and not recipient_email in recipients:
                    recipients.append(recipient_email)

                    context = MailContext(recipient)
                    if campaign.online:
                        context.update({
                            'view_online_url': reverse("campaign_view_online", kwargs={'object_id': campaign.pk}),
                            'site_url': Site.objects.get_current().domain,
                            'recipient_email': recipient_email
                        })
                    the_recipient_vars = {}
                    for k, v in context.flatten().iteritems():
                        the_recipient_vars.update({k: v})
                    recipient_vars.update({recipient_email: the_recipient_vars})

        # assemble recipient data into batches of self.BATCH_SIZE
        batches = []
        batch_r = []
        batch_v = {}
        for r in recipients:
            batch_r.append(r)
            batch_v[r] = recipient_vars[r]
            if len(batch_r) >= self.BATCH_SIZE:
                batches.append((batch_r, batch_v))
                batch_r = []
                batch_v = {}
        if len(batch_r):
            batches.append((batch_r, batch_v))

        for recipients, recipient_vars in batches:
            from_email = self.get_from_email(campaign)
            from_domain = from_email.split('@')[-1]
            from_header = self.get_from_header(campaign, from_email)
            api_url = getattr(settings, 'MAILGUN_API_URL', 'https://api.mailgun.net/v3/%s/messages') % from_domain
            auth = ("api", settings.MAILGUN_API_KEY)
            data = {
                'to': recipients,
                'from': from_header,
                'recipient-variables': json.dumps(recipient_vars),
                'subject': subject,
                'text': text_template.render(Context()),
            }

            if html_template:
                data['html'] = html_template.render(Context())

            # update data with user supplied values from settings
            data.update(getattr(settings, 'MAILGUN_API_SETTINGS', {}))

            try:
                result = requests.post(api_url, auth=auth, data=data)
                if result.status_code == 200:
                    success_count += len(recipients)
                else:
                    raise Exception(result.text)

            except Exception as e:
                logger.error('Mailgun error: %s - %s' % (e.__class__, e))
                if not fail_silently:
                    raise e

        return success_count

    def get_from_email(self, campaign):
        if hasattr(settings, 'MAILGUN_API_FROM_EMAIL'):
            from_email = settings.MAILGUN_API_FROM_EMAIL
        else:
            from_email = getattr(settings, 'CAMPAIGN_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)

        try:
            from_email = campaign.newsletter.from_email or from_email
        except:
            pass
        return from_email

    def get_from_header(self, campaign, from_email):
        try:
            from_name = campaign.newsletter.from_name or None
        except:
            from_name = None
        if from_name:
            from_header = u"%s <%s>" % (from_name, from_email)
        else:
            from_header = getattr(settings, 'CAMPAIGN_FROM_HEADERS', {}).get(from_email, from_email)
        return from_header

backend = MailgunApiBackend()
