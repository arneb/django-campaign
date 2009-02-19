from datetime import datetime
from django import template
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.mail import EmailMessage, SMTPConnection, EmailMultiAlternatives


class MailTemplate(models.Model):
    """
    Holds a template for the email. Both, HTML and plaintext, versions
    can be stored. If both are present the email will be send out as HTML 
    with an alternate plain part. If only plaintext is entered, the email will
    be send as text-only. HTML-only emails are currently not supported because
    I don't like them.
    
    """
    name = models.CharField(_(u"Name"), max_length=255)
    html = models.TextField(_(u"HTML Body"), blank=True, null=True)
    plain = models.TextField(_(u"Plaintext Body"))
    subject = models.CharField(_(u"Subject"), max_length=255)
    
    def __unicode__(self):
        return self.name
    
    

class Recipient(models.Model):
    """
    A recipient of a Mail doesn't have to correspond to a User object, but can.
    If a User object is present the email address will automatically be filled
    in, if none is given.
    
    """
    user = models.ForeignKey(User, blank=True, null=True, verbose_name=_(u"User"))
    email = models.EmailField(_(u"email address"), blank=True)
    salutation = models.CharField(_(u"salutation"), blank=True, null=True, max_length=255)
    added = models.DateTimeField(_(u"added"), editable=False)
    
    def __unicode__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.pk:
            self.added = datetime.now()
        if self.user is not None and self.email is None:
            self.email = self.user.email
        return super(Recipient, self).save(*args, **kwargs)
    
    class Meta:
        abstract = True


    
class Subscriber(Recipient):
    """
    The actual Recipient of a Mail, see Recipient docstring for more info.
    
    """

    
class Campaign(models.Model):
    """
    A Campaign is the central part of this app. Once a Campaign is created,
    has a MailTemplate and a number of Recipients, it can be send out.
    Most of the time of Campain will have a one-to-one relationship with a
    MailTemplate, but templates may be reused in other Campaigns and maybe
    Campaigns will have support for multiple templates in the future, therefore
    the distinction.
    
    """
    name = models.CharField(_(u"Name"), max_length=255)
    template = models.ForeignKey(MailTemplate, verbose_name=_(u"Template"))
    recipients = models.ManyToManyField(Subscriber, verbose_name=_(u"Subscribers"))
    sent = models.BooleanField(_(u"sent out"), default=False, editable=False)
    
    def __unicode__(self):
        return self.name
        
    def send(self):
        """
        Sends the mails to the recipients.
        """
        connection = SMTPConnection()
        
        subject = self.template.subject
        text_template = template.Template(self.template.plain)
        html_template = template.Template(self.template.html)
        
        for recipient in self.recipients.all():
            msg = EmailMultiAlternatives(subject, connection=connection, to=[recipient.email,])
            msg.body = text_template.render(template.Context({'salutation': recipient.salutation,}))
            html_content = html_template.render(template.Context({'salutation': recipient.salutation,}))
            msg.attach_alternative(html_content, 'text/html')
            msg.send()
            #print "sent one message to %s" % recipient
        
        self.sent = True
        self.save()
        #print "finished"    


class Blacklisted(Recipient):
    """
    If a user has requested removal from the subscriber-list, he is added
    to the blacklist to prevent accidential adding of the same user again.
    """
    