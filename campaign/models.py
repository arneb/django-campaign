from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.module_loading import import_string

from campaign.fields import JSONField
from campaign.backends import get_backend
from campaign.signals import campaign_sent


class Newsletter(models.Model):
    """
    Represents a recurring newsletter which users can subscribe to.

    """
    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True, null=True)
    from_email = models.EmailField(_("Sending Address"), blank=True, null=True)
    from_name = models.CharField(_("Sender Name"), max_length=255, blank=True, null=True)
    site = models.ForeignKey(Site, verbose_name=_("Site"), on_delete=models.SET_NULL, blank=True, null=True)
    default = models.BooleanField(_("Default"), default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("newsletter")
        verbose_name_plural = _("newsletters")
        ordering = ('name',)


class MailTemplate(models.Model):
    """
    Holds a template for the email. Both, HTML and plaintext, versions
    can be stored. If both are present the email will be send out as HTML
    with an alternate plain part. If only plaintext is entered, the email will
    be send as text-only. HTML-only emails are currently not supported because
    I don't like them.

    """
    name = models.CharField(_("Name"), max_length=255)
    plain = models.TextField(_("Plaintext Body"))
    html = models.TextField(_("HTML Body"), blank=True, null=True)
    subject = models.CharField(_("Subject"), max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("mail template")
        verbose_name_plural = _("mail templates")
        ordering = ('name',)


class SubscriberList(models.Model):
    """
    A pointer to another Django model which holds the subscribers.

    """
    name = models.CharField(_("Name"), max_length=255)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name=ContentType._meta.verbose_name, null=True, blank=True)
    filter_condition = JSONField(default="{}", help_text=_("Django ORM compatible lookup kwargs which are used to get the list of objects."), null=True, blank=True)
    email_field_name = models.CharField(_("Email-Field name"), max_length=64, help_text=_("Name of the model field which stores the recipients email address"))
    custom_list = models.CharField(max_length=255, choices=getattr(settings, 'CAMPAIGN_CUSTOM_SUBSCRIBER_LISTS', []), null=True, blank=True)

    def __str__(self):
        return self.name

    def _get_filter(self):
        # simplejson likes to put unicode objects as dictionary keys
        # but keyword arguments must be str type
        fc = {}
        for k, v in self.filter_condition.items():
            fc.update({str(k): v})
        return fc

    def object_list(self):
        if self.custom_list:
            return import_string(self.custom_list)().object_list()
        else:
            return self.content_type.model_class()._default_manager.filter(
                **self._get_filter()).distinct()

    def object_count(self):
        if self.custom_list:
            return import_string(self.custom_list)().object_count()
        else:
            return self.object_list().count()


    class Meta:
        verbose_name = _("subscriber list")
        verbose_name_plural = _("subscriber lists")
        ordering = ('name',)


class Campaign(models.Model):
    """
    A Campaign is the central part of this app. Once a Campaign is created,
    has a MailTemplate and one or more SubscriberLists, it can be send out.
    Most of the time of Campain will have a one-to-one relationship with a
    MailTemplate, but templates may be reused in other Campaigns and maybe
    Campaigns will have support for multiple templates in the future, therefore
    the distinction.
    A Campaign optionally belongs to a Newsletter.

    """
    name = models.CharField(_("Name"), max_length=255)
    newsletter = models.ForeignKey(Newsletter, verbose_name=_("Newsletter"), blank=True, null=True, on_delete=models.CASCADE)
    template = models.ForeignKey(MailTemplate, verbose_name=_("Template"), on_delete=models.CASCADE)
    recipients = models.ManyToManyField(SubscriberList, verbose_name=_("Subscriber lists"))
    sent = models.BooleanField(_("sent out"), default=False, editable=False)
    sent_at = models.DateTimeField(_("sent at"), blank=True, null=True)
    online = models.BooleanField(_("available online"), default=True, blank=True, help_text=_("make a copy available online"))

    def __str__(self):
        return self.name

    def send(self, subscriber_lists=None):
        """
        Sends the mails to the recipients.
        """
        backend = get_backend()
        num_sent = backend.send_campaign(self, subscriber_lists=subscriber_lists)
        self.sent = True
        self.sent_at = timezone.now()
        self.save()
        campaign_sent.send(sender=self.__class__, campaign=self)
        return num_sent

    class Meta:
        verbose_name = _("campaign")
        verbose_name_plural = _("campaigns")
        ordering = ('name', 'sent')
        permissions = (
            ("send_campaign", _("Can send campaign")),
        )


class BlacklistEntry(models.Model):
    """
    If a user has requested removal from the subscriber-list, he is added
    to the blacklist to prevent accidential adding of the same user again
    on subsequent imports from a data source.
    """
    email = models.EmailField()
    added = models.DateTimeField(default=timezone.now, editable=False)
    reason = models.TextField(_("reason"), blank=True, null=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _("blacklist entry")
        verbose_name_plural = _("blacklist entries")
        ordering = ('-added',)
