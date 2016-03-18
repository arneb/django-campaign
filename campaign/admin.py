from django.shortcuts import render_to_response
from django import template
from django import forms
try:
    from django.utils.functional import update_wrapper
except ImportError:
    from functools import update_wrapper
from django.conf.urls import patterns, url
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin.util import unquote
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

import swapper

from campaign.models import MailTemplate, Campaign, BlacklistEntry, \
SubscriberList, Newsletter


class CampaignAdmin(admin.ModelAdmin):
    filter_horizontal=('recipients',)
    list_display=('name', 'newsletter', 'sent', 'sent_at', 'online')
    send_template = None

    def has_send_permission(self, request, obj):
        """
        Subclasses may override this and implement more granular permissions.
        TODO: integrate with django's permisson system
        """
        return request.user.is_superuser


    def send_view(self, request, object_id, extra_context=None):
        """
        Allows the admin to send out the mails for this campaign.
        """
        model = self.model
        opts = model._meta

        try:
            obj = model._default_manager.get(pk=unquote(object_id))
        except model.DoesNotExist:
            # Don't raise Http404 just yet, because we haven't checked
            # permissions yet. We don't want an unauthenticated user to be able
            # to determine whether a given object exists.
            obj = None

        if not self.has_send_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})

        if request.method == 'POST':
            if not request.POST.get('send', None) == '1':
                raise PermissionDenied

            num_sent = obj.send()
            messages.success(request, _(u'The %(name)s "%(obj)s" was successfully sent. %(num_sent)s messages delivered.' %  {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj), 'num_sent': num_sent,}))
            return HttpResponseRedirect('../')


        def form_media():
            css = ['css/forms.css',]
            return forms.Media(css={'screen': ['%sadmin/%s' % (settings.STATIC_URL, url) for url in css]})

        media = self.media + form_media()

        context = {
            'title': _('Send %s') % force_unicode(opts.verbose_name),
            'object_id': object_id,
            'object': obj,
            'is_popup': request.REQUEST.has_key('_popup'),
            'media': mark_safe(media),
            'app_label': opts.app_label,
            'opts': opts,
        }
        context.update(extra_context or {})

        return render_to_response(self.send_template or
            ['admin/%s/%s/send_object.html' % (opts.app_label, opts.object_name.lower()),
            'admin/%s/send_object.html' % opts.app_label,
            'admin/send_object.html'], context, context_instance=template.RequestContext(request))


    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.admin_site.name, self.model._meta.app_label, self.model._meta.module_name

        super_urlpatterns = super(CampaignAdmin, self).get_urls()
        urlpatterns = patterns('',
            url(r'^(.+)/send/$',
                wrap(self.send_view),
                name='%sadmin_%s_%s_send' % info),
        )
        urlpatterns += super_urlpatterns

        return urlpatterns


class BlacklistEntryAdmin(admin.ModelAdmin):
    list_display=('email', 'added')

    def fetch_mandrill_rejects(self, request):
        call_command('fetch_mandrill_rejects')
        msg = _("Successfully fetched Mandrill rejects")
        self.message_user(request, msg, messages.SUCCESS)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", '..'))


    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.admin_site.name, self.model._meta.app_label, self.model._meta.module_name

        super_urlpatterns = super(BlacklistEntryAdmin, self).get_urls()
        urlpatterns = patterns('',
            url(r'^fetch_mandrill_rejects/$',
                wrap(self.fetch_mandrill_rejects),
                name='%sadmin_%s_%s_fetchmandrillrejects' % info),
        )
        urlpatterns += super_urlpatterns

        return urlpatterns


if not swapper.is_swapped('campaign', 'Campaign'):
    admin.site.register(Campaign, CampaignAdmin)

admin.site.register(MailTemplate)
admin.site.register(BlacklistEntry, BlacklistEntryAdmin)
admin.site.register(SubscriberList)
admin.site.register(Newsletter, list_display=('name', 'from_email'))
