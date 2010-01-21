from datetime import datetime
from django import template
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from campaign.fields import JSONField
from campaign.context import MailContext
from campaign.backends import backend


class MailTemplate(models.Model):
    """
    Holds a template for the email. Both, HTML and plaintext, versions
    can be stored. If both are present the email will be send out as HTML 
    with an alternate plain part. If only plaintext is entered, the email will
    be send as text-only. HTML-only emails are currently not supported because
    I don't like them.
    
    """
    name = models.CharField(_(u"Name"), max_length=255)
    plain = models.TextField(_(u"Plaintext Body"))
    html = models.TextField(_(u"HTML Body"), blank=True, null=True)
    subject = models.CharField(_(u"Subject"), max_length=255)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _("mail template")
        verbose_name_plural = _("mail templates")
        ordering = ('name',)


class SubscriberList(models.Model):
    """
    A pointer to another Django model which holds the subscribers.
    
    """
    name = models.CharField(_(u"Name"), max_length=255)
    content_type = models.ForeignKey(ContentType)
    filter_condition = JSONField(default="{}", help_text=_(u"Django ORM compatible lookup kwargs which are used to get the list of objects."))
    email_field_name = models.CharField(_(u"Email-Field name"), max_length=64, help_text=_(u"Name of the model field which stores the recipients email address"))
    
    def __unicode__(self):
        return self.name
        
    def _get_filter(self):
        # simplejson likes to put unicode objects as dictionary keys
        # but keyword arguments must be str type
        fc = {}
        for k,v in self.filter_condition.iteritems():
            fc.update({str(k): v})
        return fc
        
    def object_list(self):
        return self.content_type.model_class()._default_manager.filter(**self._get_filter())
        
    def object_count(self):
        return self.content_type.model_class()._default_manager.filter(**self._get_filter()).count()
            
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
    
    """
    name = models.CharField(_(u"Name"), max_length=255)
    template = models.ForeignKey(MailTemplate, verbose_name=_(u"Template"))
    recipients = models.ManyToManyField(SubscriberList, verbose_name=_(u"Subscriber lists"))
    sent = models.BooleanField(_(u"sent out"), default=False, editable=False)
    online = models.BooleanField(_(u"available online"), default=True, blank=True, help_text=_(u"make a copy available online"))
    
    def __unicode__(self):
        return self.name
            
        
    def send(self):
        """
        Sends the mails to the recipients.
        """
        num_sent = self._send()
        self.sent = True
        self.save()
        return num_sent
        
        
    def _send(self):
        """
        Does the actual work
        """    
        subject = self.template.subject
        text_template = template.Template(self.template.plain)
        if self.template.html is not None and self.template.html != u"":
            html_template = template.Template(self.template.html)
        
        sent = 0
        used_addresses = []
        for recipient_list in self.recipients.all():
            for recipient in recipient_list.object_list():
                # never send mail to blacklisted email addresses
                recipient_email = getattr(recipient, recipient_list.email_field_name)
                if not BlacklistEntry.objects.filter(email=recipient_email).count() and not recipient_email in used_addresses:
                    msg = EmailMultiAlternatives(subject, to=[recipient_email,])
                    context = MailContext(recipient)
                    if self.online:
                        context.update({'view_online_url': reverse("campaign_view_online", kwargs={'object_id': self.pk}),
                                        'site_url': Site.objects.get_current().domain,
                                        'recipient_email': recipient_email})
                    msg.body = text_template.render(context)
                    if self.template.html is not None and self.template.html != u"":
                        html_content = html_template.render(context)
                        msg.attach_alternative(html_content, 'text/html')
                    sent += backend.send_mail(msg)
                    used_addresses.append(recipient_email)
        return sent

    class Meta:
        verbose_name = _("campaign")
        verbose_name_plural = _("campaigns")
        ordering = ('name', 'sent')


class BlacklistEntry(models.Model):
    """
    If a user has requested removal from the subscriber-list, he is added
    to the blacklist to prevent accidential adding of the same user again
    on subsequent imports from a data source.
    """
    email = models.EmailField()
    added = models.DateTimeField(default=datetime.now, editable=False)
    
    def __unicode__(self):
        return self.email
        
    class Meta:
        verbose_name = _("blacklist entry")
        verbose_name_plural = _("blacklist entries")
        ordering = ('-added',)    


class BounceEntry(models.Model):
    """
    Records bouncing Recipients. To be processed by a human.
    """
    email = models.CharField(_(u"recipient"), max_length=255, blank=True, null=True)
    exception = models.TextField(_(u"exception"), blank=True, null=True)
    
    def __unicode__(self):
        return self.email
        
    class Meta:
        verbose_name = _("bounce entry")
        verbose_name_plural = _("bounce entries")
        ordering = ('email',)
        

    