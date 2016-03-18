# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .backends import get_backend


class CampaignAbstract(models.Model):

    name = models.CharField(_("name"), max_length=255)
    newsletter = models.ForeignKey(
        'campaign.Newsletter', verbose_name=_("newsletter"), blank=True, null=True)
    template = models.ForeignKey('campaign.MailTemplate', verbose_name=_("template"))

    recipients = models.ManyToManyField(
        'campaign.SubscriberList', verbose_name=_("subscriber lists"))

    sent = models.BooleanField(_("sent out"), default=False, editable=False)
    sent_at = models.DateTimeField(_("sent at"), blank=True, null=True)

    online = models.BooleanField(_("available online"), default=True, blank=True,
        help_text=_("make a copy available online"))

    class Meta:
        abstract = True
        verbose_name = _("campaign")
        verbose_name_plural = _("campaigns")
        ordering = ('name', 'sent')

    def __unicode__(self):
        return self.name

    def send(self):
        """
        Sends the mails to the recipients.
        """
        backend = get_backend()
        num_sent = backend.send_campaign(self)
        self.sent = True
        self.sent_at = timezone.now()
        self.save()
        return num_sent

