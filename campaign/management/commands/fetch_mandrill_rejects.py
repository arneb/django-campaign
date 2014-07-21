import logging
import mandrill
from django.conf import settings
from django.core.management.base import NoArgsCommand
from campaign.models import BlacklistEntry

logger = logging.getLogger('django.campaign')


class Command(NoArgsCommand):
    """
    This command fetches all rejects from the Mandrill API and stores them
    in the local blacklist. This ensures that campaign doesn't send a mail to a
    bad recipient address more than once and that helps improving
    the deliverability rate.

    This command assumes that your Mandrill API-Key is configured in::

        settings.MANDRILL_API_KEY

    """
    help = "fetch rejects from mandrill and store in local blacklist"

    def handle_noargs(self, **options):
        try:
            mandrill_client = mandrill.Mandrill(settings.MANDRILL_API_KEY)
            rejects = mandrill_client.rejects.list()

            for reject in rejects:
                if reject['reason'] in ('hard-bounce', 'spam', 'unsub'):
                    defaults = {'reason': u"%s: %s" % (reject['reason'],
                                                       reject['detail'])}
                    BlacklistEntry.objects.get_or_create(email=reject['email'],
                                                         defaults=defaults)

        except mandrill.Error, e:
            logger.error('Mandrill error: %s - %s' % (e.__class__, e))
            raise e
