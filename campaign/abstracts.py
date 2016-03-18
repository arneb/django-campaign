# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


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

    def __unicode__(self):
        return self.name
