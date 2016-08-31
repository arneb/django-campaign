import logging
import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from campaign.models import BlacklistEntry

logger = logging.getLogger('django.campaign')


class Command(BaseCommand):
    """
    This command fetches all bounces from the Mailgun API and stores them
    in the local blacklist. This ensures that campaign doesn't send a mail to a
    bad recipient address more than once and that helps improving
    the deliverability rate.

    This backend assumes, that your Mailgun API-Key is configured in::

        settings.MAILGUN_API_KEY

    Additionally you need to set all domains, for which bounces should
    be collected in::

        settings.MAILGUN_DOMAINS

    """
    help = "fetch bounces from mailgun and store in local blacklist"

    def handle(self, *args, **options):
        processed = 0
        valid = 0
        domain_list = getattr(settings, 'MAILGUN_DOMAINS', [])

        if not len(domain_list):
            raise CommandError('you need to confgure the MAILGUN_DOMAINS setting')

        for domain in domain_list:
            try:
                api_url = getattr(settings, 'MAILGUN_API_URL', 'https://api.mailgun.net/v3/%s/bounces') % domain
                x, y = self._fetch_rejects(api_url)
                processed += x
                valid += y
            except Exception as e:
                logger.error('Mailgun error: %s - %s' % (e.__class__, e))
                raise CommandError(e)

        self.stdout.write("processed: %s" % processed)
        self.stdout.write("valid: %s" % valid)

    def _fetch_rejects(self, url):
        processed = 0
        valid = 0

        auth = ("api", settings.MAILGUN_API_KEY)
        response = requests.get(url, auth=auth)

        if response.status_code == 200:
            for reject in response.json()['items']:
                processed += 1
                if int(reject['code']) >= 500:
                    valid += 1
                    BlacklistEntry.objects.get_or_create(
                        email=reject['address'],
                        defaults={'reason': reject['error']}
                    )
        else:
            logger.warning('Mailgun response: %s' % result.status_code)

        pagination = response.json()["paging"]
        if pagination.get("next") != pagination.get("previous"):
            x, y = self._fetch_rejects(pagination.get("next"))
            processed += x
            valid += y

        return processed, valid
